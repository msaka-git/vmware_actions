#!/usr/bin/env python3
import sys
import atexit
import ssl
from pyVim import connect
from pyVmomi import vim
import time

class vsphere:
    def __init__(self,esxhost, user, password):
        self.esxhost=esxhost
        self.user=user
        self.password=password
        self.vconnect()
    def vconnect(self):

        s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        s.verify_mode = ssl.CERT_NONE  # disable ssl verification

        service_instance = connect.SmartConnect(host=self.esxhost,  # build python connection to vSphere
                                                user=self.user,
                                                pwd=self.password,
                                                sslContext=s)
        atexit.register(connect.Disconnect, service_instance)  # build disconnect logic

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(container, viewType, recursive)  # create container view
        global children
        children = containerView.view


    def take_snap():
        for child in children:  # for each statement to iterate all names of VMs in the environment
            summary = child.summary
            if summary.config.name == sys.argv[2].upper():

                task_snp=child.CreateSnapshot_Task(name=sys.argv[3],description=sys.argv[4],memory=True,quiesce=False)
                print("Snapshot is ongoing")
                tp=''
                while True:
                    print('Waiting for snap completion...')
                    time.sleep(20)
                    try:

                      snap_info=child.snapshot
                      snapshots=child.snapshot.rootSnapshotList
                      tp=type(snapshots)
                      for s in snapshots:
                          snap_obj=s.snapshot
                          print(snap_obj)
                      print(snap_info)
                      print('*************SNAPSHOT IS DONE********************')
                      break
                    except AttributeError:
                      print('Still wating..')
                      if tp!='':
                          for s in snapshots:
                              snap_obj=s.snapshot
                              print(snap_obj)
                          print('*************SNAPSHOT IS DONE********************')
                          print(snap_info)
                          break


    def delete_snap():
        for child in children:
            summary = child.summary

            if summary.config.name == sys.argv[2].upper():

                print("Searching for snapshot...")
                tp = ''
                while True:
                    print("Removing snapshot")
                    time.sleep(20)
                    try:

                        snap_info = child.snapshot
                        snapshots = child.snapshot.rootSnapshotList
                        tp = type(snapshots)
                        for s in snapshots:
                            snap_obj = s.snapshot
                            print(snap_obj)
                            snap_obj.RemoveSnapshot_Task(True)
                            print('*************SNAPSHOT HAS BEEN REMOVED********************')
                        break
                    except AttributeError:
                        print('Still wating..')
                        if tp == '':

                            print('*************NO SNAPSHOT FOUND********************')

                            break

    def poweron():
        for child in children:
            summary = child.summary

            if summary.config.name == sys.argv[2].upper():

                child.PowerOnVM_Task()
                print("Powered on {}...".format(sys.argv[2].upper()))

    def poweroff():
        for child in children:
            summary = child.summary

            if summary.config.name == sys.argv[2].upper():
                child.PowerOffVM_Task()
                print("Powered off {}...".format(sys.argv[2].upper()))

    def add_disk():
        for child in children:
            summary = child.summary
            if summary.config.name == sys.argv[2].upper():
                spec = vim.vm.ConfigSpec() ### Get all actual configs
                d=child.config.hardware.device # get all disks on a VM, set unit_number to the next available
                unit_number = 0
                for dev in d:
                      if hasattr(dev.backing, 'fileName'):
                            unit_number = int(dev.unitNumber) + 1
                            print("unit_numer is:" + str(unit_number))
                            # unit_number 7 reserved for scsi controller, not possible to add more than 15 disks.
                            if unit_number == 7:
                                  unit_number += 1
                            if unit_number >= 16:
                                  print("we don't support this many disks")
                                  return
                      if isinstance(dev, vim.vm.device.VirtualSCSIController):
                            controller = dev
                            print("controller: " + str(controller))

                # add disk here arg 3 is disk size
                dev_changes = []
                new_disk_kb = int(sys.argv[3]) * 1024 * 1024
                disk_spec = vim.vm.device.VirtualDeviceSpec()
                disk_spec.fileOperation = "create"
                disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
                disk_spec.device = vim.vm.device.VirtualDisk()
                disk_spec.device.backing = \
                vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                #if sys.argv[4] == 'thin':
                disk_spec.device.backing.thinProvisioned = True
                disk_spec.device.backing.diskMode = 'persistent'
                disk_spec.device.unitNumber = unit_number
                disk_spec.device.capacityInKB = new_disk_kb
                disk_spec.device.controllerKey = controller.key
                dev_changes.append(disk_spec)
                spec.deviceChange = dev_changes
                child.ReconfigVM_Task(spec=spec)
                print("%sGB disk added to %s" % (sys.argv[3], child.config.name))


    def del_disk():
        for child in children:
            summary = child.summary
            if summary.config.name == sys.argv[2].upper():

               hdd_prefix_label = 'Hard disk '
               if not hdd_prefix_label:
                  raise RuntimeError('Hdd prefix label could not be found')

               hdd_label = hdd_prefix_label + str(sys.argv[3])
               print(hdd_label)
               virtual_hdd_device = None
               print(virtual_hdd_device)

               for dev in child.config.hardware.device:
                   if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == hdd_label:
                        virtual_hdd_device = dev
               if not virtual_hdd_device:
                   raise RuntimeError('Virtual {} could not be found.'.format(virtual_hdd_device))

               virtual_hdd_spec = vim.vm.device.VirtualDeviceSpec()
               virtual_hdd_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
               virtual_hdd_spec.device = virtual_hdd_device

               spec = vim.vm.ConfigSpec()
               spec.deviceChange = [virtual_hdd_spec]
               task = child.ReconfigVM_Task(spec=spec)
               print(task)
               print('***** DISK %s REMOVED FROM %s ******' % (sys.argv[3],child.config.name))

    def snap_list():

        for child in children:

            summary = child.summary
            try:

                if summary.config.name == sys.argv[2].upper():
                    snapshot_data = []
                    snap_text = ""
                    snap_info = child.snapshot
                    snapshots = child.snapshot.rootSnapshotList
                    for snapshot in snapshots:
                        print("\n###### SNAPSHOT FOUND ######\n")
                        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
                            snapshot.name, snapshot.description,
                            snapshot.createTime, snapshot.state)
                        snapshot_data.append(snap_text)
                        print(snapshot_data)

            except AttributeError:
                print("\n******* NO SNAPSHOT FOUND ********\n")

    def snap_list_all():
        tp_list = []
        for child in children:

            summary = child.summary
            hostname = summary.config.name
            if summary.config.name == hostname:
                snapshot_data = []
                snap_text = ""
                snap_info = child.snapshot
                if snap_info != None:
                    snapshots = snap_info.rootSnapshotList
                    for snapshot in snapshots:
                        print("\n###### SNAPSHOT FOUND: {}  ######\n".format(hostname))
                        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
                            snapshot.name, snapshot.description,
                            snapshot.createTime, snapshot.state)
                        snapshot_data.append(snap_text)
                        print(snapshot_data)


### Modify below params according to your credentials and Vcenter

Vsphere=vsphere('esxhost','vsphere login','vsphere pass')
try:

    if sys.argv[1] == 'snap':
        vsphere.take_snap()
    elif sys.argv[1] == 'del':
        vsphere.delete_snap()
    elif sys.argv[1] == 'on':
        vsphere.poweron()
    elif sys.argv[1] == 'off':
        vsphere.poweroff()
    elif sys.argv[1] == 'diskadd':
        vsphere.add_disk()
    elif sys.argv[1] == 'diskdel':
        vsphere.del_disk()
    elif sys.argv[1] == 'snaplist':
        vsphere.snap_list()
    elif sys.argv[1] == 'snaplistall':
        vsphere.snap_list_all()
except IndexError:
    print('\noption1 : snap (to take snapshot) - del (to delete snapshot) - on (poweron a guest) - off (poweroff a guest) - diskadd (to add disk) - diskdel (to delete disk)\n')
    print('option2 : hostname\n')
    print('option3,4 : Depends on what you want to do. Check examples.\n')
    print('Usage Exmaples:\n')
    print('Take Snapshot: python3 vmware_ops.py snap hostname reboot patching -----(reboot : name of snapshot, patching : snap description)\n'
          'Delete snapshot: python3 vmware_ops.py del hostname\n'
          'To add a disk: test_api.py diskadd hostname 1 ---(1 is the size in GB)---\n'
          'To delete a disk: test_api.py diskdel hostname 3 ---(3 is disk number to delete)---\n'
          'Poweron / poweroff ex: vmware_ops.py on(or off) hostname\n'
          'Search snapshot by hostname: vmware_ops.py snaplist hostname\n'
          'Search all snapshots: vmware_ops.py snaplistall\n')
