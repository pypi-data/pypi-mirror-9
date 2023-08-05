#
# Copyright (C) 2013-2014 eNovance SAS <licensing@enovance.com>
#
# Author: Frederic Lepied <frederic.lepied@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

'''Functions to match according to a requirement specification.'''

import logging
import re
import sys
try:
    import ipaddr
    _HAS_IPADDR = True
except ImportError:
    _HAS_IPADDR = False

_FUNC_REGEXP = re.compile(r'^(.*)\((.*)\)')

LOG = logging.getLogger('hardware.matcher')


def _adder(array, index, value):
    'Auxiliary function to add a value to an array.'
    array[index] = value


def _appender(array, index, value):
    'Auxiliary function to append a value to an array.'
    try:
        array[index].append(value)
    except KeyError:
        array[index] = [value, ]


def _gt(left, right):
    'Helper for match_spec.'
    return int(left) > int(right)


def _ge(left, right):
    'Helper for match_spec.'
    return int(left) >= int(right)


def _lt(left, right):
    'Helper for match_spec.'
    return int(left) < int(right)


def _le(left, right):
    'Helper for match_spec.'
    return int(left) <= int(right)


def _network(left, right):
    'Helper for match_spec.'
    if _HAS_IPADDR:
        return ipaddr.IPv4Address(left) in ipaddr.IPv4Network(right)
    else:
        return False


def _regexp(left, right):
    'Helper for match_spec.'
    print(left, right)
    return re.search(right, left) is not None


def _in(elt, _list):
    'Helper for match_spec.'
    # build a list from the string or return False
    try:
        lst = eval('(' + _list + ')')
    except Exception:
        return False
    # cast into an int or do nothing
    try:
        elt = int(elt)
    except ValueError:
        pass
    return elt in lst


def match_spec(spec, lines, arr, adder=_adder):
    'Match a line according to a spec and store variables in <var>.'
    # match a line without variable
    for idx in range(len(lines)):
        if lines[idx] == spec:
            res = lines[idx]
            del lines[idx]
            return res
    # match a line with a variable, a function or both
    for lidx in range(len(lines)):
        line = lines[lidx]
        varidx = []
        for idx in range(4):
            # try to split the variable and function parts if we have both
            if spec[idx][0] == '$':
                parts = spec[idx].split('=')
                if len(parts) == 2:
                    var, func = parts
                    matched = False
                else:
                    var = func = spec[idx]
            else:
                var = func = spec[idx]
            # Match a function
            if func[-1] == ')':
                res = _FUNC_REGEXP.search(func)
                if res:
                    func_name = '_' + res.group(1)
                    if func_name in globals():
                        if not globals()[func_name](line[idx], res.group(2)):
                            if var == func:
                                break
                        else:
                            if var == func:
                                continue
                            matched = True
                    else:
                        if var == func:
                            break
            # Match a variable
            if ((var == func) or (var != func and matched)) and var[0] == '$':
                if adder == _adder and var[1:] in arr:
                    if arr[var[1:]] != line[idx]:
                        break
                varidx.append((idx, var[1:]))
            # Match the full string
            elif line[idx] != spec[idx]:
                break
        else:
            for i, var in varidx:
                adder(arr, var, line[i])
            res = lines[lidx]
            del lines[lidx]
            return res
    return False


def match_all(lines, specs, arr, arr2, debug=False, level=0):
    '''Match all lines according to a spec.

Store variables starting with a $ in <arr>. Variables starting with
2 $ like $$vda are stored in arr and arr2.
'''
    # Work on a copy of lines to avoid changing the real lines because
    # match_spec removes the matched line to not match it again on next
    # calls.
    lines = list(lines)
    specs = list(specs)
    copy_arr = dict(arr)
    points = []
    # Prevent infinit loops
    if level == 50:
        return False
    # Match lines using specs
    while len(specs) > 0:
        copy_specs = list(specs)
        spec = specs.pop(0)
        line = match_spec(spec, lines, arr)
        # No match
        if not line:
            # Backtrack on the backtracking points
            while len(points) > 0:
                lines, specs, new_arr = points.pop()
                if match_all(lines, specs, new_arr, arr2, debug, level + 1):
                    # Copy arr back
                    for k in new_arr:
                        arr[k] = new_arr[k]
                    return True
            if level == 0 and debug:
                sys.stderr.write('spec: %s not matched\n' % str(spec))
            return False
        else:
            # Store backtraking points when we find a new variable
            if arr != copy_arr:
                copy_lines = list(lines)
                # Put the matching line at the end of the lines
                copy_lines.append(line)
                points.append((copy_lines, copy_specs, copy_arr))
                copy_arr = arr
    # Manage $$ variables
    for key in arr:
        if key[0] == '$':
            nkey = key[1:]
            arr[nkey] = arr[key]
            arr2[nkey] = arr[key]
            del arr[key]
    return True


def match_multiple(lines, spec, arr):
    'Use spec to find all the matching lines and gather variables.'
    ret = False
    lines = list(lines)
    while match_spec(spec, lines, arr, adder=_appender):
        ret = True
    return ret


def generate_filename_and_macs(items):
    '''Generate a file name for a hardware using DMI information.

(product name and version) then if the DMI serial number is
available we use it unless we lookup the first mac address.
As a result, we do have a filename like :

<dmi_product_name>-<dmi_product_version>-{dmi_serial_num|mac_address}
'''

    # Duplicate items as it will be modified by match_* functions
    hw_items = list(items)
    sysvars = {}
    sysvars['sysname'] = ''

    match_spec(('system', 'product', 'vendor', '$sysprodvendor'),
               hw_items, sysvars)

    if 'sysprodvendor' in sysvars:
        sysvars['sysname'] += (re.sub(r'\W+', '', sysvars['sysprodvendor']) +
                               '-')

    match_spec(('system', 'product', 'name', '$sysprodname'),
               hw_items, sysvars)

    if 'sysprodname' in sysvars:
        sysvars['sysname'] = re.sub(r'\W+', '', sysvars['sysprodname']) + '-'

    match_spec(('system', 'product', 'serial', '$sysserial'),
               hw_items, sysvars)

    # Let's use any existing DMI serial number or take the first mac address
    if 'sysserial' in sysvars:
        sysvars['sysname'] += re.sub(r'\W+', '', sysvars['sysserial'])

    # we always need to have the mac addresses for pxemngr
    if match_multiple(hw_items,
                      ('network', '$eth', 'serial', '$serial'),
                      sysvars):
        if 'sysserial' not in sysvars:
            sysvars['sysname'] += sysvars['serial'][0].replace(':', '-')
    else:
        LOG.warning('unable to detect network macs')

    return sysvars

# matcher.py ends here
