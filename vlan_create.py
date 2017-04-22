import netmiko 
import sys, json
from copy import copy

if len(sys.argv) < 2:
    print('Usage: vlan_create.py [PASSWORD]')
    exit()

with open('device_list.json') as device_list:
    all_devices = json.load(device_list)

with open('vlan_to_create.json') as vlan_to_create:
    new_vlans = json.load(vlan_to_create)

creationTask = []
output = [ "##################################", "OUTPUT FROM COMMANDSET", "##################################"]

for vlan in new_vlans:
    for hostname in vlan['switches']:
        for device in all_devices:
	    if device['hostname'] == hostname:
                device['vlanid'] = vlan['vlanid']
                device['bridge_pri'] = vlan['root_bridge_pri']
                device['bridge_sec'] = vlan['root_bridge_sec']                
                device['vlan_name'] = vlan['name']
                creationTask.append(device.copy())


for switch in creationTask:
    if device['driver'] == 'ios':
        device_type = 'cisco_ios'
    else:
        print('Device is not supported, skipping ' + device['hostname'] )
        continue
    
    vlanString = 'vlan ' + switch['vlanid']
    nameString = 'name ' + switch['vlan_name']
    commandSet = [ vlanString, nameString]
    if switch['hostname'] == switch['bridge_pri']:
        commandSet.append('spanning-tree vlan ' + switch['vlanid'] + ' priority 4096')
    elif switch['hostname'] == switch['bridge_sec']:
        commandSet.append('spanning-tree vlan ' + switch['vlanid'] + ' priority 8192')


    print ('Connecting to : ' + switch['ip'])
    print ('~'*79)
    connection = netmiko.ConnectHandler(device_type=device_type,username=switch['username'],ip=switch['ip'],password=sys.argv[1])
    print ('Executing the following commands: ')
    for command in commandSet:
        print(command)
    output.append(connection.send_config_set(commandSet))

for entry in output:
    print(entry)

