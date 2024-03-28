from pyVmomi import vim
from pyVim.task import WaitForTask
from pyVim.connect import SmartConnect, Disconnect
import ssl
import logging
import utility.nic2dvs as nic
from utility.full_info import full_info

vsphere_ip = "10.250.0.50"
vsphere_user = "administrator@vsphere.local"
vsphere_pass = "Aruba123!@#"

logging.basicConfig(filename="nick.log",
    				format='%(asctime)s %(message)s',
    				filemode='a')

sslContext = ssl._create_unverified_context()

port="443"



# Create a connector to vsphere
service_instance = SmartConnect(
                    host=vsphere_ip,
                    user=vsphere_user,
                    pwd=vsphere_pass,
                    port=port,
                    sslContext=sslContext
)
if service_instance:

    content = service_instance.RetrieveContent()
    # read list of dictionaries in full_info.py file.
    for i in full_info:
        print(i)
        switch = nic.find_dvs_by_name(content, i['switch'])
        # Get switch UUID
        i['switch_uuid'] = switch.uuid

        portgroup = nic.find_dvs_portgroup_by_name(content, i['switch'], i['group'])
        if portgroup:
            vm = nic.find_vm_by_name(content, i['load'])
            if vm:
                trash, portgroup_key = str(portgroup).split(':')
                portgroup_key = portgroup_key[:-1]

                response = nic.connect_vnic_to_portgroup(vm,
                                                         portgroup_key,
                                                         i['vmnic_mac'],
                                                         i['switch_uuid'],
                                                         i['group'],
                                                         i['portKey'])

Disconnect(service_instance)
