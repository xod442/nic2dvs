import utility.nic2dvs as nic

dvs_name = 'LG01-dvs-1'
dvs_pg = 'LG01-DP-01'
vm_name ='LG01-WL01-V10-101'
vmnic_mac = '00:50:56:b6:5c:a6'
portKey = '1'
vsp_ip = '10.250.0.50'
vsp_user = 'administrator@vsphere.local'
vsp_pass = "password"

response = nic.connect_vnic_to_portgroup(dvs_name,dvs_pg,vm_name,vmnic_mac,portKey,vsp_ip,vsp_user,vsp_pass)
