'''
supporting functions about database side group management
'''
from cloudmesh.cm_mongo import cm_mongo
from cloudmesh.experiment.group import GroupManagement
from cloudmesh.cm_mongo import cm_mongo


def add_vm_to_group_while_creating(username, groupname, vmname):
    '''
    add a vm to a group while the vm is being created, if the group doesn't exist, 
    this will create one
    '''
    GroupManage = GroupManagement(username)
    groups_list = GroupManage.get_groups_names_list()
    if groupname not in groups_list:
        GroupManage.create_group(groupname)
    GroupManage.add_item_to_group(groupname, "VM", vmname)


def remove_vm_from_group_while_deleting(username, vmname):
    '''
    remove a vm from the group, assume there is no duplicate vm names, so
    this function will simplt remove all vms with name vmname from group
    database
    '''
    GroupManage = GroupManagement(username)
    res = GroupManage.get_same_items_from_all_groups("VM", vmname)
    for item in res:
        item.delete()


def get_group_names_list_by_vms_metadata(username, cloudname, refresh=False):
    '''
    loops through all VMs of a cloud of a user, returns a list of all unique group 
    names accorrding to the metadata
    '''
    mongo = cm_mongo()
    if refresh:
        mongo.activate(cm_user_id=username, names=[cloudname])
        mongo.refresh(cm_user_id=username,
                      names=[cloudname],
                      types=['servers'])
    servers_dict = mongo.servers(
        clouds=[cloudname],
        cm_user_id=username)[cloudname]
                
    res = []
    for k, v in servers_dict.iteritems():
        if 'cm_group' in v['metadata']:
            temp = v['metadata']['cm_group']
            if temp not in res:
                res.append(temp)
    
    return res


def add_item_to_group(username, groupname, _type, value, refresh=False):
    '''
    this is a more spicific function to add items to groups, e.g. using command group add item
    NAME VM VALUE, check whether vm exists before add it to group
    '''
    GroupManage = GroupManagement(username)
    # if type is VM, check whether the VM exists, in this case, value is the VM name
    if _type.upper() == "VM":
        mongo = cm_mongo()
        if refresh:
            mongo.activate(cm_user_id=username)
            mongo.refresh(cm_user_id=username, types=['servers'])
        servers_dict = mongo.servers(cm_user_id=username)
        _vm_exists = False
        for k, v in servers_dict.iteritems():
            for k0, v0 in v.iteritems():
                if 'name' in v0 and v0['name'] == value:
                    _vm_exists = True
                    break
            if _vm_exists:
                break
        if _vm_exists:
            GroupManage.add_item_to_group(groupname, _type, value)
        else:
            raise Exception("VM '{0}' doesn't exist".format(value))
    else:
        GroupManage.add_item_to_group(groupname, _type, value)