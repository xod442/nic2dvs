from pyVmomi import vim
from pyVim.task import WaitForTask
import time

import logging

def list_dvs_switches(content):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    dvs_list = dvs_view.view
    dvs_view.Destroy()
    return dvs_list

def wait_for_task(task, hideResult=False):
    """
    Waits and provides updates on a vSphere task
    """
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(5)
    return task.info.result

def get_dvswitches_and_portgroups(content):
    """
    Retrieve all distributed virtual switches and their associated port groups in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = {'uuid': switch.uuid, 'portgroups': []}
        for pg in switch.portgroup:
            dvswitches[switch.name]['portgroups'].append(pg.name)
    container.Destroy()
    return dvswitches


def get_dvswitches_and_uplinks(content):
    """
    Retrieve all distributed virtual switches and their associated uplinks in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = {'uuid': switch.uuid, 'uplinks': []}
        for uplink in switch.config.uplinkPortgroup:
            dvswitches[switch.name]['uplinks'].append(uplink.name)
    container.Destroy()
    return dvswitches

def get_dvswitches(content):
    """
    Retrieve all distributed virtual switches in the vCenter Server.
    """
    dvswitches = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in container.view:
        dvswitches[switch.name] = switch.uuid
    container.Destroy()
    return dvswitches

def list_networks(content):
    network_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)
    networks = network_view.view
    network_view.Destroy()
    return networks


# Function to find a virtual machine by its name
def find_vm_by_name(content, vm_name):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm.name == vm_name:
            return vm
    return None

# Function to find a distributed virtual switch by its name
def find_dvs_by_name(content, dvs_name):
    dvs_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualSwitch], True)
    for switch in dvs_view.view:
        if switch.name == dvs_name:
            return switch
    return None

def get_dvportgroup_names(service_instance):
    content = service_instance.RetrieveContent()
    dvportgroups = content.viewManager.CreateContainerView(content.rootFolder, [vim.DistributedVirtualPortgroup], True)

    dvportgroup_names = []
    for dvportgroup in dvportgroups.view:
        dvportgroup_names.append(dvportgroup.name)

    return dvportgroup_names


def find_dvs_portgroup_by_name(content, dvs_name, portgroup_name):
    dvs = find_dvs_by_name(content, dvs_name)
    if dvs:
        #print(dvs_name)
        portgroup = find_portgroup_by_name(content, dvs, portgroup_name)
        return portgroup
    else:
        return None

def find_portgroup_by_name(content, dvs, portgroup_name):
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    portgroups = [pg for pg in portgroup_view.view if pg.config.distributedVirtualSwitch == dvs and pg.name == portgroup_name]
    portgroup_view.Destroy()
    if portgroups:
        return portgroups[0]
    else:
        return None

def connect_vnic_to_portgroup(vm, portgroup_key, vmnic_mac, switch_uuid, portgroup_name, portKey):
    '''
    variable: vm  type: vmware object description: USe function -find_vm_by_name- and pass the string of the workloads vm_name
    variable: portgroup_key type: string description: Use -find_dvs_portgrpup_by_name function
    variable: vmnic_mac  type: string description: macc address of vm port.
    variable: switch_uuid type: string 
    '''
    devices = vm.config.hardware.device
    for device in devices:

        if isinstance(device, vim.vm.device.VirtualVmxnet3):
            if str(device.macAddress) == vmnic_mac:
                nic_spec = vim.vm.device.VirtualDeviceSpec()
                nic_spec.device = device
                nic_spec.device.connectable.connected = True
                nic_spec.device.deviceInfo.summary = portgroup_name
                nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                nic_spec.device.backing.port.switchUuid = switch_uuid
                nic_spec.device.backing.port.portgroupKey = portgroup_key
                nic_spec.device.backing.port.portKey = portKey

                config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
                # Connect the port
                task_number = vm.ReconfigVM_Task(config_spec)
                response = wait_for_task(task_number)
                print("Successfully connected vNIC with MAC {} to DVS port group.".format(vmnic_mac))
                return


        #print("No vNIC found with MAC {} on the VM.".format(vmnic_mac))

    return None
