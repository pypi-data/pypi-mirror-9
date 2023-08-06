#
# Copyright (C) 2013-2015 eNovance SAS <licensing@enovance.com>
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

'''Main entry point for hardware and system detection routines in eDeploy.'''


import argparse
import fcntl
import json
import os
import pprint
import re
import socket
import struct
from subprocess import PIPE
from subprocess import Popen
import sys
import xml.etree.ElementTree as ET

from netaddr import IPNetwork

from hardware.benchmark import cpu as bm_cpu
from hardware.benchmark import disk as bm_disk
from hardware.benchmark import mem as bm_mem
from hardware import detect_utils
from hardware.detect_utils import cmd
from hardware import diskinfo
from hardware import hpacucli
from hardware import infiniband as ib
from hardware import ipmi
from hardware import megacli

SIOCGIFNETMASK = 0x891b


def size_in_gb(size):
    'Return the size in GB without the unit.'
    ret = size.replace(' ', '')
    if ret[-2:] == 'GB':
        return ret[:-2]
    elif ret[-2:] == 'TB':
        # some size are provided in x.yGB
        # we need to compute the size in TB by
        # considering the input as a float to be
        # multiplied by 1000
        return str(int(float(ret[:-2]) * 1000))
    else:
        return ret


def detect_hpa(hw_lst):
    'Detect HP RAID controller configuration.'
    disk_count = 0
    try:
        cli = hpacucli.Cli(debug=False)
        if not cli.launch():
            return False
        controllers = cli.ctrl_all_show()
        if len(controllers) == 0:
            sys.stderr.write("Info: No hpa controller found\n")
            return False

    except hpacucli.Error as expt:
        sys.stderr.write('Info: detect_hpa : %s\n' % expt.value)
        return False

    hw_lst.append(('hpa', "slots", "count", str(len(controllers))))
    global_pdisk_size = 0
    for controller in controllers:
        try:
            slot = 'slot=%d' % controller[0]
            controllers_infos = cli.ctrl_show(slot)
            for controller_info in controllers_infos.keys():
                hw_lst.append(('hpa', slot.replace('=', '_'),
                               controller_info,
                               controllers_infos[controller_info]))
            for _, disks in cli.ctrl_pd_all_show(slot):
                for disk in disks:
                    disk_count += 1
                    hw_lst.append(('disk', disk[0], 'type', disk[1]))
                    hw_lst.append(('disk', disk[0], 'slot',
                                   str(controller[0])))
                    disk_infos = cli.ctrl_pd_disk_show(slot, disk[0])
                    for disk_info in disk_infos.keys():
                        value = disk_infos[disk_info]
                        if disk_info == "size":
                            value = size_in_gb(disk_infos[disk_info])
                            global_pdisk_size = (global_pdisk_size +
                                                 float(value))
                        hw_lst.append(('disk', disk[0], disk_info,
                                       value))
        except hpacucli.Error as expt:
            sys.stderr.write('Info: detect_hpa : controller %d : %s\n'
                             % (controller[0], expt.value))

    if global_pdisk_size > 0:
        hw_lst.append(('disk', 'hpa', 'size', "%.2f" % global_pdisk_size))

    hw_lst.append(('disk', 'hpa', 'count', str(disk_count)))
    return True


def detect_megacli(hw_lst):
    'Detect LSI MegaRAID controller configuration.'
    ctrl_num = megacli.adp_count()
    disk_count = 0
    global_pdisk_size = 0
    if ctrl_num > 0:
        for ctrl in range(ctrl_num):
            ctrl_info = megacli.adp_all_info(ctrl)
            for entry in ctrl_info.keys():
                hw_lst.append(('megaraid', 'Controller_%d' % (ctrl),
                               '%s' % entry, '%s' % ctrl_info[entry]))

            for enc in megacli.enc_info(ctrl):
                if "Enclosure" in enc.keys():
                    for key in enc.keys():
                        if "ExitCode" in key or "Enclosure" in key:
                            continue
                        hw_lst.append(('megaraid',
                                       'Controller_%d/Enclosure_%s' %
                                       (ctrl, enc["Enclosure"]),
                                       '%s' % key, '%s' % enc[key]))

                for slot_num in range(enc['NumberOfSlots']):
                    disk = 'disk%d' % slot_num
                    info = megacli.pdinfo(ctrl,
                                          enc['DeviceId'],
                                          slot_num)

                    # If no PdType, it means that's not a disk
                    if 'PdType' not in info.keys():
                        continue

                    disk_count += 1
                    hw_lst.append(('pdisk',
                                   disk,
                                   'ctrl',
                                   str(ctrl_num)))
                    hw_lst.append(('pdisk',
                                   disk,
                                   'type',
                                   info['PdType']))
                    hw_lst.append(('pdisk',
                                   disk,
                                   'id',
                                   '%s:%d' % (info['EnclosureDeviceId'],
                                              slot_num)))
                    disk_size = size_in_gb("%s %s" %
                                           (info['CoercedSize'].split()[0],
                                            info['CoercedSize'].split()[1]))
                    global_pdisk_size = global_pdisk_size + float(disk_size)
                    hw_lst.append(('pdisk',
                                   disk,
                                   'size',
                                   disk_size))

                    for key in info.keys():
                        ignore_list = ['PdType', 'EnclosureDeviceId',
                                       'CoercedSize', 'ExitCode']
                        if key not in ignore_list:
                            if "DriveTemperature" in key:
                                if "C" in str(info[key].split()[0]):
                                    pdisk = info[key].split()[0].split("C")[0]
                                    hw_lst.append(('pdisk', disk, key,
                                                   str(pdisk).strip()))
                                    hw_lst.append(('pdisk', disk,
                                                   "%s_units" % key,
                                                   "Celsius"))
                                else:
                                    hw_lst.append(('pdisk', disk, key,
                                                   str(info[key]).strip()))

                            elif "InquiryData" in key:
                                count = 0
                                for mystring in info[key].split():
                                    hw_lst.append(('pdisk', disk,
                                                   "%s[%d]" % (key, count),
                                                   str(mystring.strip())))
                                    count = count + 1

                            else:
                                hw_lst.append(('pdisk', disk, key,
                                               str(info[key]).strip()))

                if global_pdisk_size > 0:
                    hw_lst.append(('pdisk',
                                   'all',
                                   'size',
                                   "%.2f" % global_pdisk_size))

                for ld_num in range(megacli.ld_get_num(ctrl)):
                    disk = 'disk%d' % ld_num
                    info = megacli.ld_get_info(ctrl, ld_num)
                    hw_lst.append(('ldisk',
                                   disk,
                                   'current_access_policy',
                                   info['CurrentAccessPolicy']))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'current_cache_policy',
                                   info['CurrentCachePolicy']))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'disk_cache_policy',
                                   info['DiskCachePolicy']))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'name',
                                   info['Name']))
                    try:
                        hw_lst.append(('ldisk',
                                       disk,
                                       'number_of_drives',
                                       str(info['NumberOfDrives'])))
                    except KeyError:
                        pass
                    try:
                        hw_lst.append(('ldisk',
                                       disk,
                                       'number_of_drives_per_span',
                                       str(info['NumberOfDrivesPerSpan'])))
                    except KeyError:
                        pass
                    hw_lst.append(('ldisk',
                                   disk,
                                   'raid_level',
                                   info['RaidLevel']))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'sector_size',
                                   str(info['SectorSize'])))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'state',
                                   info['State']))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'Size',
                                   size_in_gb(info['Size'])))
                    hw_lst.append(('ldisk',
                                   disk,
                                   'strip_size',
                                   info['StripSize']))
        hw_lst.append(('disk', 'megaraid', 'count', str(disk_count)))
        return True
    else:
        return False


def detect_disks(hw_lst):
    'Detect disks.'
    names = diskinfo.disknames()
    sizes = diskinfo.disksizes(names)
    disks = [name for name, size in sizes.items() if size > 0]
    hw_lst.append(('disk', 'logical', 'count', str(len(disks))))
    for name in disks:
        hw_lst.append(('disk', name, 'size', str(sizes[name])))
        item_list = ['device/vendor', 'device/model', 'device/rev',
                     'queue/optimal_io_size', 'queue/physical_block_size',
                     'queue/rotational']
        for my_item in item_list:
            try:
                with open('/sys/block/%s/%s' % (name, my_item), 'r') as dev:
                    hw_lst.append(('disk', name, my_item.split('/')[1],
                                   dev.readline().rstrip('\n').strip()))
            except Exception as excpt:
                sys.stderr.write(
                    'Failed at getting disk information '
                    'at /sys/block/%s/device/%s: %s\n' % (name,
                                                          my_item,
                                                          str(excpt)))

        item_list = ['WCE', 'RCD']
        item_def = {'WCE': 'Write Cache Enable', 'RCD': 'Read Cache Disable'}
        for my_item in item_list:
            sdparm_cmd = Popen("sdparm -q --get=%s /dev/%s | "
                               "awk '{print $2}'" % (my_item, name),
                               shell=True,
                               stdout=PIPE)
            for line in sdparm_cmd.stdout:
                hw_lst.append(('disk', name, item_def.get(my_item),
                               line.rstrip('\n').strip()))

        # In some VMs, the disk-by id doesn't exists
        if os.path.exists('/dev/disk/by-id/'):
            for entry in os.listdir('/dev/disk/by-id/'):
                idp = os.path.realpath('/dev/disk/by-id/' + entry).split('/')
                if idp[-1] == name:
                    id_name = "id"
                    if entry.startswith('wwn'):
                        id_name = "wwn-id"
                    elif entry.startswith('scsi'):
                        id_name = "scsi-id"
                    hw_lst.append(('disk', name, id_name, entry))

        detect_utils.read_SMART(hw_lst, "/dev/%s" % name)


def modprobe(module):
    'Load a kernel module using modprobe.'
    status, _ = cmd('modprobe %s' % module)
    if status == 0:
        sys.stderr.write('Info: Probing %s failed\n' % module)


def detect_ipmi(hw_lst):
    'Detect IPMI interfaces.'
    modprobe("ipmi_smb")
    modprobe("ipmi_si")
    modprobe("ipmi_devintf")
    if (os.path.exists('/dev/ipmi0') or os.path.exists('/dev/ipmi/0') or
       os.path.exists('/dev/ipmidev/0')):
        for channel in range(0, 16):
            status, _ = cmd('ipmitool channel info %d 2>&1 | grep -sq Volatile'
                            % channel)
            if status == 0:
                hw_lst.append(('system', 'ipmi', 'channel', '%s' % channel))
                break
        status, output = cmd('ipmitool lan print')
        if status == 0:
            ipmi.parse_lan_info(output, hw_lst)
    else:
        # do we need a fake ipmi device for testing purpose ?
        status, _ = cmd('grep -qi FAKEIPMI /proc/cmdline')
        if status == 0:
            # Yes ! So let's create a fake entry
            hw_lst.append(('system', 'ipmi-fake', 'channel', '0'))
            sys.stderr.write('Info: Added fake IPMI device\n')
            return True
        else:
            sys.stderr.write('Info: No IPMI device found\n')
            return False


def get_cidr(netmask):
    'Convert a netmask to a CIDR.'
    binary_str = ''
    for octet in netmask.split('.'):
        binary_str += bin(int(octet))[2:].zfill(8)
    return str(len(binary_str.rstrip('0')))


def detect_infiniband(hw_lst):
    '''Detect Infiniband devinces.

To detect if an IB device is present, we search for a pci device.
This pci device shall be from vendor Mellanox (15b3) form class 0280
Class 280 stands for a Network Controller while ethernet device are 0200.
'''
    status, _ = cmd("lspci -d 15b3: -n|awk '{print $2}'|grep -q '0280'")
    if status == 0:
        ib_card = 0
        for devices in range(ib_card, len(ib.ib_card_drv())):
            card_type = ib.ib_card_drv()[devices]
            ib_infos = ib.ib_global_info(card_type)
            nb_ports = ib_infos['nb_ports']
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'card_type', card_type))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'device_type', ib_infos['device_type']))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'fw_version', ib_infos['fw_ver']))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'hw_version', ib_infos['hw_ver']))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'nb_ports', nb_ports))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'sys_guid', ib_infos['sys_guid']))
            hw_lst.append(('infiniband', 'card%i' % ib_card,
                           'node_guid', ib_infos['node_guid']))
            for port in range(1, int(nb_ports) + 1):
                ib_port_infos = ib.ib_port_info(card_type, port)
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'state', ib_port_infos['state']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'physical_state',
                               ib_port_infos['physical_state']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'rate', ib_port_infos['rate']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'base_lid', ib_port_infos['base_lid']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'lmc', ib_port_infos['lmc']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'sm_lid', ib_port_infos['sm_lid']))
                hw_lst.append(('infiniband', 'card%i_port%i' % (ib_card, port),
                               'port_guid', ib_port_infos['port_guid']))
        return True
    else:
        sys.stderr.write('Info: No Infiniband device found\n')
        return False


def get_uuid():
    'Get uuid from dmidecode'
    uuid_cmd = Popen("dmidecode -t 1 | grep UUID | "
                     "awk '{print $2}'",
                     shell=True,
                     stdout=PIPE)
    return uuid_cmd.stdout.read().rstrip()


def _get_value(hw_lst, *vect):
    for i in hw_lst:
        if i[0:3] == vect:
            return i[3]
    return ''


def detect_system(hw_lst, output=None):
    'Detect system characteristics from the output of lshw.'

    socket_count = 0

    def find_element(xml, xml_spec, sys_subtype,
                     sys_type='product', sys_cls='system',
                     attrib=None, transform=None):
        'Lookup an xml element and populate hw_lst when found.'
        elt = xml.findall(xml_spec)
        if len(elt) >= 1:
            if attrib:
                txt = elt[0].attrib[attrib]
            else:
                txt = elt[0].text
            if transform:
                txt = transform(txt)
            hw_lst.append((sys_cls, sys_type, sys_subtype, txt))
            return txt
        return None

    # handle output injection for testing purpose
    if output:
        status = 0
    else:
        status, output = cmd('lshw -xml')
    if status == 0:
        mobo_id = ''
        nic_id = ''
        xml = ET.fromstring(output)
        find_element(xml, "./node/serial", 'serial')
        find_element(xml, "./node/product", 'name')
        find_element(xml, "./node/vendor", 'vendor')
        find_element(xml, "./node/version", 'version')
        uuid = get_uuid()

        if uuid:
            # If we have an uuid, we shall check if it's part of a
            # known list of broken uuid
            # If so let's delete the uuid instead of reporting a stupid thing
            if uuid in ['Not']:
                uuid = ''
            else:
                hw_lst.append(('system', 'product', 'uuid', uuid))

        for elt in xml.findall(".//node[@id='core']"):
            name = elt.find('physid')
            if name is not None:
                find_element(elt, 'product', 'name', 'motherboard', 'system')
                find_element(elt, 'vendor', 'vendor', 'motherboard', 'system')
                find_element(elt, 'version', 'version', 'motherboard',
                             'system')
                find_element(elt, 'serial', 'serial', 'motherboard', 'system')
                mobo_id = _get_value(hw_lst, 'system', 'motherboard', 'serial')

        for elt in xml.findall(".//node[@id='firmware']"):
            name = elt.find('physid')
            if name is not None:
                find_element(elt, 'version', 'version', 'bios', 'firmware')
                find_element(elt, 'date', 'date', 'bios', 'firmware')
                find_element(elt, 'vendor', 'vendor', 'bios', 'firmware')

        bank_count = 0
        for elt in xml.findall(".//node[@class='memory']"):
            if not elt.attrib['id'].startswith('memory'):
                continue
            try:
                location = re.search('memory(:.*)', elt.attrib['id']).group(1)
            except AttributeError:
                location = ''
            name = elt.find('physid')
            if name is not None:
                find_element(elt, 'size', 'size', 'total', 'memory')
                for bank_list in elt.findall(".//node[@id]"):
                    if 'bank:' in bank_list.get('id'):
                        bank_count = bank_count + 1
                        for bank in elt.findall(".//node[@id='%s']" %
                                                (bank_list.get('id'))):
                            bank_id = bank_list.get('id').replace("bank:",
                                                                  "bank" +
                                                                  location +
                                                                  ":")
                            find_element(bank, 'size', 'size',
                                         bank_id, 'memory')
                            find_element(bank, 'clock', 'clock',
                                         bank_id, 'memory')
                            find_element(bank, 'description', 'description',
                                         bank_id, 'memory')
                            find_element(bank, 'vendor', 'vendor',
                                         bank_id, 'memory')
                            find_element(bank, 'product', 'product',
                                         bank_id, 'memory')
                            find_element(bank, 'serial', 'serial',
                                         bank_id, 'memory')
                            find_element(bank, 'slot', 'slot',
                                         bank_id, 'memory')
        if bank_count > 0:
            hw_lst.append(('memory', 'banks', 'count', str(bank_count)))

        for elt in xml.findall(".//node[@class='network']"):
            name = elt.find('logicalname')
            if name is not None:
                find_element(elt, 'businfo', 'businfo', name.text, 'network')
                find_element(elt, 'vendor', 'vendor', name.text, 'network')
                find_element(elt, 'product', 'product', name.text, 'network')
                find_element(elt, "configuration/setting[@id='firmware']",
                             'firmware', name.text, 'network', 'value')
                find_element(elt, 'size', 'size', name.text, 'network')
                ipv4 = find_element(elt, "configuration/setting[@id='ip']",
                                    'ipv4',
                                    name.text, 'network', 'value')
                if ipv4 is not None:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        netmask = socket.inet_ntoa(
                            fcntl.ioctl(
                                sock, SIOCGIFNETMASK,
                                struct.pack('256s',
                                            name.text.encode('utf-8')))[20:24])
                        hw_lst.append(
                            ('network', name.text, 'ipv4-netmask', netmask))
                        cidr = get_cidr(netmask)
                        hw_lst.append(
                            ('network', name.text, 'ipv4-cidr', cidr))
                        hw_lst.append(
                            ('network', name.text, 'ipv4-network',
                             "%s" % IPNetwork('%s/%s' % (ipv4, cidr)).network))
                    except Exception as excpt:
                        sys.stderr.write('unable to get info for %s: %s\n'
                                         % (name.text, str(excpt)))

                find_element(elt, "configuration/setting[@id='link']", 'link',
                             name.text, 'network', 'value')
                find_element(elt, "configuration/setting[@id='driver']",
                             'driver', name.text, 'network', 'value')
                find_element(elt, "configuration/setting[@id='duplex']",
                             'duplex', name.text, 'network', 'value')
                find_element(elt, "configuration/setting[@id='speed']",
                             'speed', name.text, 'network', 'value')
                find_element(elt, "configuration/setting[@id='latency']",
                             'latency', name.text, 'network', 'value')
                find_element(elt,
                             "configuration/setting[@id='autonegotiation']",
                             'autonegotiation', name.text, 'network', 'value')

                # lshw is not able to get the complete mac addr for ib
                # devices Let's workaround it with an ip command.
                if name.text.startswith('ib'):
                    cmds = "ip addr show %s | grep link | awk '{print $2}'"
                    status_ip, output_ip = cmd(cmds % name.text)
                    if status_ip == 0:
                        hw_lst.append(('network',
                                       name.text,
                                       'serial',
                                       output_ip.split('\n')[0].lower()))
                else:
                    find_element(elt, 'serial', 'serial', name.text, 'network',
                                 transform=lambda x: x.lower())

                if not nic_id:
                    nic_id = _get_value(hw_lst, 'network',
                                        name.text, 'serial')
                    nic_id = nic_id.replace(':', '')

                detect_utils.get_ethtool_status(hw_lst, name.text)
                detect_utils.get_lld_status(hw_lst, name.text)

        for elt in xml.findall(".//node[@class='processor']"):
            name = elt.find('physid')
            if name is not None:
                hw_lst.append(('cpu', 'physical_%s' % (socket_count),
                               'physid', name.text))
                find_element(elt, 'product', 'product',
                             'physical_%s' % socket_count, 'cpu')
                find_element(elt, 'vendor', 'vendor',
                             'physical_%s' % socket_count, 'cpu')
                find_element(elt, 'version', 'version',
                             'physical_%s' % socket_count, 'cpu')
                find_element(elt, 'size', 'frequency',
                             'physical_%s' % socket_count, 'cpu')
                find_element(elt, 'clock', 'clock',
                             'physical_%s' % socket_count, 'cpu')
                find_element(elt, "configuration/setting[@id='cores']",
                             'cores', 'physical_%s' % socket_count,
                             'cpu', 'value')
                find_element(elt, "configuration/setting[@id='enabledcores']",
                             'enabled_cores', 'physical_%s' % socket_count,
                             'cpu', 'value')
                find_element(elt, "configuration/setting[@id='threads']",
                             'threads', 'physical_%s' % socket_count, 'cpu',
                             'value')

                elt_cap = elt.findall("capabilities/capability")
                cpu_flags = ""
                for cap in elt_cap:
                    for element in cap.items():
                        cpu_flags = "%s %s" % (cpu_flags, element[1].strip())

                hw_lst.append(('cpu', 'physical_%s' % (socket_count),
                               'flags', cpu_flags.strip()))

                socket_count = socket_count + 1

        fix_bad_serial(hw_lst, uuid, mobo_id, nic_id)

    else:
        sys.stderr.write("Unable to run lshw: %s\n" % output)
        return False

    hw_lst.append(('cpu', 'physical', 'number', str(socket_count)))
    status, output = detect_utils.cmd('nproc')
    if status == 0:
        hw_lst.append(('cpu', 'logical', 'number', str(output).strip()))

    osvendor_cmd = detect_utils.output_lines("lsb_release -is")
    for line in osvendor_cmd:
        hw_lst.append(('system', 'os', 'vendor', line.rstrip('\n').strip()))

    osinfo_cmd = detect_utils.output_lines("lsb_release -ds | tr -d '\"'")
    for line in osinfo_cmd:
        hw_lst.append(('system', 'os', 'version', line.rstrip('\n').strip()))

    uname_cmd = detect_utils.output_lines("uname -r")
    for line in uname_cmd:
        hw_lst.append(('system', 'kernel', 'version',
                       line.rstrip('\n').strip()))

    arch_cmd = detect_utils.output_lines("uname -i")
    for line in arch_cmd:
        hw_lst.append(('system', 'kernel', 'arch', line.rstrip('\n').strip()))

    cmdline_cmd = detect_utils.output_lines("cat /proc/cmdline")
    for line in cmdline_cmd:
        hw_lst.append(('system', 'kernel', 'cmdline',
                       line.rstrip('\n').strip()))
    return True


def fix_bad_serial(hw_lst, uuid, mobo_id, nic_id):
    'Fix bad serial number'
    # Let's manage a quirk list of stupid serial numbers TYAN
    # or Supermicro are known to provide dirty serial numbers
    # In that case, let's use another serial
    for i in hw_lst:
        if i[0:3] == ('system', 'product', 'serial'):
            # Does the current serial number is part of the quirk list
            if i[3] in ['0123456789', '0000000000']:

                # Let's delete the stupid SN and use the another ID instead
                # Items are ordered by level of confidence
                new_serial = ''

                if uuid:
                    new_serial = uuid
                elif mobo_id:
                    new_serial = mobo_id
                elif nic_id:
                    new_serial = nic_id

                if new_serial:
                    hw_lst.remove(i)
                    hw_lst.append(('system', 'product', 'serial',
                                  new_serial))

                break


def read_hwmon(hwlst, entry, sensor, label_name, appendix, processor_num,
               entry_name):
    try:
        hwmon = "%s_%s" % (sensor, appendix)
        filename = "/sys/devices/platform/%s/%s" % (entry, hwmon)
        if not os.path.isfile(filename):
            if len(hwmon) > 16:
                # Some kernels are shortening the filename to 17 chars
                # Let's try to find if we are in this case
                filename = "/sys/devices/platform/%s/%s" % (entry, hwmon[:16])
                if not os.path.isfile(filename):
                    sys.stderr.write("read_hwmon: No entry found for %s/%s\n" %
                                     (label_name, entry_name))
                    return
            else:
                sys.stderr.write("read_hwmon: No entry found for %s/%s\n" %
                                 (label_name, entry_name))
                return

        value = open(filename, 'r').readline().strip()
        hwlst.append(('cpu', 'physical_%d' % processor_num, "%s/%s" %
                      (label_name, entry_name), value))
    except Exception:
        pass


def detect_temperatures(hwlst):
    for entry in os.listdir("/sys/devices/platform/"):
        if entry.startswith("coretemp."):
            processor_num = int(entry.split(".")[1])
            for label in os.listdir("/sys/devices/platform/%s" % entry):
                if label.startswith("temp") and label.endswith("_label"):
                    sensor = label.split("_")[0]
                    try:
                        with open("/sys/devices/platform/%s/%s_label" %
                                  (entry, sensor), 'r') as fsensor:
                            label_name = fsensor.readline()
                            label_name = label_name.strip().replace(" ", "_")
                    except Exception:
                        sys.stderr.write("detect_temperatures: "
                                         "Cannot open label on %s/%s\n" %
                                         (entry, sensor))
                        continue

                    read_hwmon(hwlst, entry, sensor, label_name, "input",
                               processor_num, "temperature")
                    read_hwmon(hwlst, entry, sensor, label_name, "max",
                               processor_num, "max")
                    read_hwmon(hwlst, entry, sensor, label_name, "crit",
                               processor_num, "critical")
                    read_hwmon(hwlst, entry, sensor, label_name, "crit_alarm",
                               processor_num, "critical_alarm")


def parse_ahci(hrdw, words):
    if len(words) < 4:
        return
    if "flags" in words[2]:
        flags = ""
        for flag in sorted(words[3:]):
            flags = "%s %s" % (flags, flag)
        hrdw.append(('ahci', words[1], "flags", flags.strip()))


def parse_dmesg(hrdw, output):
    for line in output.split('\n'):
        words = line.strip().split(" ")

        if words[0].startswith("[") and words[0].endswith("]"):
            words = words[1:]

        if not words:
            continue

        if "ahci" in words[0]:
            parse_ahci(hrdw, words)


def _main(options):
    'Command line entry point.'
    hrdw = []
    detect_hpa(hrdw)
    detect_megacli(hrdw)
    detect_disks(hrdw)
    if not detect_system(hrdw):
        sys.exit(1)
    detect_ipmi(hrdw)
    detect_infiniband(hrdw)
    detect_temperatures(hrdw)
    detect_utils.get_ddr_timing(hrdw)
    detect_utils.ipmi_sdr(hrdw)
    _, output = cmd("dmesg")
    parse_dmesg(hrdw, output)

    if "benchmark_cpu" in options:
        bm_cpu.cpu_perf(hrdw)

    if "benchmark_mem" in options:
        bm_mem.mem_perf(hrdw)

    if "benchmark_disk" in options:
        bm_disk.disk_perf(hrdw,
                          destructive=options['benchmark_disk_destructive'])

    if "human" in options.keys():
        pprint.pprint(hrdw)
    else:
        print(json.dumps(hrdw))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--human',
                        help='Print output in human readable format',
                        action='store_true',
                        default=False)
    parser.add_argument('--benchmark', '-b',
                        help=('Run benchmark for specific components. '
                              'Valid components are: disk, cpu, mem'),
                        metavar='component',
                        nargs='+')
    parser.add_argument('--benchmark-disk-destructive',
                        help=('If specified make the disk component benchmark '
                              'to be destructive'),
                        action='store_true',
                        default=False)

    options = {}
    args = parser.parse_args()
    if args.human:
        options["human"] = True
    if args.benchmark:
        invalid_opts = []
        for opt in args.benchmark:
            opt_ = opt.lower()
            if opt_ == 'cpu':
                options['benchmark_cpu'] = True
            elif opt_ == 'mem':
                options['benchmark_mem'] = True
            elif opt_ == 'disk':
                options['benchmark_disk'] = True
                options['benchmark_disk_destructive'] = (
                    args.benchmark_disk_destructive)
            else:
                invalid_opts.append(opt)

        if invalid_opts:
            print('"%s" is/are not valid benchmark component(s). Check '
                  '--help to see the list of acceptable values' %
                  ', '.join(invalid_opts))
            sys.exit(1)

    _main(options)
