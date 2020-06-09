# from __future__ import print_function
# from vconnector.core import VConnector

import atexit
import ssl
from pyVim import connect
from pyVmomi import vim

'''
client = VConnector(
    user='8002894@IRC.MPW.FRA',
    pwd='M@npower!2019administrator',
    host='10.0.32.184')
client.connect()
vms = client.get_vm_view()
print(vms.view)
'''


### For vmware api, python2.7 should be used (dependency for pyVmomi vim)

def vconnect():
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE  # disable our certificate checking for lab

    service_instance = connect.SmartConnect(host="pr-hostvm-01.irc.mpw.fra",  # build python connection to vSphere
                                            user="8002894@IRC.MPW.FRA",
                                            pwd="M@npower!2019administrator",
                                            sslContext=s)

    atexit.register(connect.Disconnect, service_instance)  # build disconnect logic

    content = service_instance.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)  # create container view
    children = containerView.view

    for child in children:  # for each statement to iterate all names of VMs in the environment
        summary = child.summary
        # print(summary.config.name)
        # print("Virtual Machine Name:        "+summary.config.name)
        # print("Virtual Machine OS:          "+summary.config.guestFullName)
        # print("")
        if summary.config.name == 'IRACOUBO_NEW':
            print(summary)
            # child.PowerOnVM_Task()
            # print('Powered on IRACOUBO_NEW')
            # task_snp=child.CreateSnapshot_Task(name='snapshot',description='patching',memory=True,quiesce=False)
            # print("Snapshot OK")
            snap_info = child.snapshot
            snapshots = child.snapshot.rootSnapshotList
            print(type(snapshots))
            for s in snapshots:
                snap_obj = s.snapshot
                print(snap_obj)
                # print("Removing snapshot")
                # snap_obj.RemoveSnapshot_Task(True)
            print(snap_info)


vconnect()