# vmware_actions
Action for Vsphere; take/delete snapshots, poweroff/on VMs,add/delete disks

For now it is able do following actions:

- Power on/off guest VMs on ESX host,

- Take / Delete VM snapshots

- Add / delete new disk to guest VM

- Search snapshot on all guests or by hostname

To run the script you will need python 3 and following libraries installed:

 * atexit
 * ssl
 * PyVim
 * PyVmomi 


Usage is: 

Around line 191 you will find this :

Vsphere=vsphere('esxhost','vsphere login','vsphere pass')

change esx host/ cluster name of your own, ex: vmcluxter.irc.mpman.it and  update Vshpere client credentials.

#/usr/bin/env python3 shebang is set. In linux with chmod +x vmware_ops.py command you can run without addind python3 in the beginning of your command line.

Take Snapshot: 

python3 vmware_ops.py snap hostname reboot patching -----(reboot : name of snapshot, you can give any name, patching : snap description, you can write any description)

Delete snapshot:
 
python3 vmware_ops.py del hostname

To add a disk:

python3 vmware_ops.py diskadd hostname 1 ---(1 is the size in GB)---

To delete a disk: 

python3 vmware_ops.py diskdel hostname 3 ---(3 is disk number to delete)---

Poweron / poweroff ex: 

python3 vmware_ops.py on(or off) hostname
