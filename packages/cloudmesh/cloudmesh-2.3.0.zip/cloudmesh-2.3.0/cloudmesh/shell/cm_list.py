from __future__ import print_function
from cloudmesh.config.cm_config import cm_config
from cloudmesh.shell.cm_cloud import CloudManage
from cloudmesh_base.logger import LOGGER
from tabulate import tabulate
from cmd3.console import Console
from cloudmesh.shell.cm_cloud import shell_command_cloud
from docopt import docopt
from cloudmesh.shell.shellutil import shell_commands_dict_output, get_command_list_refresh_default_setting
from pprint import pprint

# list_command_table_format = "simple"
list_command_table_format = "grid"

log = LOGGER(__file__)


def shell_command_list(arguments):
    """
    ::

      List available flavors, images, vms, projects and clouds

      Usage:
          list flavor [CLOUD|--all] 
                      [--refresh] 
                      [--format=FORMAT]
                      [--column=COLUMN]
          list image [CLOUD|--all] 
                     [--refresh] 
                     [--format=FORMAT] 
                     [--column=COLUMN]
          list vm [CLOUD|--all] 
                  [--group=<group>]
                  [--refresh] 
                  [--format=FORMAT] 
                  [--column=COLUMN] 
                  [--detail]
          list project
          list cloud [--column=COLUMN]

      Arguments:

          CLOUD    the name of the cloud e.g. india

      Options:

          --all                  list information of all active clouds
          --refresh              refresh data before list
          --group=<group>        give the group name in list vm
          --detail               for table print format, a brief version 
                                 is used as default, use this flag to print
                                 detailed table
          --column=COLUMN        specify what information to display in
                                 the columns of the list command. For
                                 example, --column=active,label prints
                                 the columns active and label. Available
                                 columns are active, label, host,
                                 type/version, type, heading, user,
                                 credentials, defaults (all to display
                                 all, email to display all except
                                 credentials and defaults)
          --format=FORMAT        output format: table, json, csv

      Description:

          List clouds and projects information, if the CLOUD argument is not specified, the
          selected default cloud will be used. You can interactively set the default cloud with the command
          'cloud select'.

          list flavor
          : list the flavors
          list image
          : list the images
          list vm
          : list the vms
          list project
          : list the projects
          list cloud
          : same as cloud list

      See Also:

          man cloud

    """
    call = ListInfo(arguments)
    call.execute()


class ListInfo(object):

    def __init__(self, arguments):
        self.cloudmanage = CloudManage()
        try:
            self.config = cm_config()
        except:
            Console.error("There is a problem with the configuration yaml files")

        self.username = self.config['cloudmesh']['profile']['username']

        self.arguments = arguments
        
        # pprint(self.arguments)
        
        self.cloudmanage = CloudManage()
        try:
            self.config = cm_config()
        except:
            Console.error("There is a problem with the configuration yaml files")
    
        self.username = self.config['cloudmesh']['profile']['username']
        self.refresh_default_setting = get_command_list_refresh_default_setting(self.username)

    def _list_flavor(self):
        self.cloudmanage._connect_to_mongo()
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = [
                ['id', 'id'],
                ['name', 'name'],
                ['vcpus', 'vcpus'],
                ['ram', 'ram'],
                ['disk', 'disk'],
                ['refresh time', 'cm_refresh']
            ]
            if self.refresh_default_setting or self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(
                    cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(
                    cm_user_id=self.username, names=clouds, types=['flavors'])

            # --format
            p_format = self.arguments['--format']

            # --column
            # available columns are: id, name, vcpus, ram, disk, refresh time,
            # and all

            if self.arguments['--column']:
                if self.arguments['--column'] != "all":
                    s_column = [x.strip() for x in
                                self.arguments['--column'].split(',')]
                    new_itemkeys = []
                    for item in itemkeys:
                        if item[0] in s_column:
                            new_itemkeys.append(item)
                    itemkeys = new_itemkeys

            for cloud in clouds:
                self.cloudmanage.print_cloud_flavors(username=self.username,
                                                     cloudname=cloud.encode(
                                                         "ascii"),
                                                     itemkeys=itemkeys,
                                                     refresh=False,
                                                     output=False,
                                                     print_format=p_format)
        else:
            return

    def _list_image(self):
        self.cloudmanage._connect_to_mongo()
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = {"openstack":
                        [
                            # [ "Metadata", "metadata"],
                            ["name", "name"],
                            ["status", "status"],
                            ["id", "id"],
                            ["type_id", "metadata", "instance_type_id"],
                            ["iname", "metadata", "instance_type_name"],
                            ["location", "metadata", "image_location"],
                            ["state", "metadata", "image_state"],
                            ["updated", "updated"],
                            # [ "minDisk" , "minDisk"],
                            ["memory_mb", "metadata",
                                'instance_type_memory_mb'],
                            ["fid", "metadata", "instance_type_flavorid"],
                            ["vcpus", "metadata", "instance_type_vcpus"],
                            # [ "user_id" , "metadata", "user_id"],
                            # [ "owner_id" , "metadata", "owner_id"],
                            # [ "gb" , "metadata", "instance_type_root_gb"],
                            # [ "arch", ""]
                        ],
                        "ec2":
                        [
                            # [ "Metadata", "metadata"],
                            ["state", "extra", "state"],
                            ["name", "name"],
                            ["id", "id"],
                            ["public", "extra", "is_public"],
                            ["ownerid", "extra", "owner_id"],
                            ["imagetype", "extra", "image_type"]
                        ],
                        "azure":
                        [
                            ["name", "label"],
                            ["category", "category"],
                            ["id", "id"],
                            ["size", "logical_size_in_gb"],
                            ["os", "os"]
                        ],
                        "aws":
                        [
                            ["state", "extra", "state"],
                            ["name", "name"],
                            ["id", "id"],
                            ["public", "extra", "ispublic"],
                            ["ownerid", "extra", "ownerid"],
                            ["imagetype", "extra", "imagetype"]
                        ]
                        }
            if self.refresh_default_setting or self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(
                    cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(
                    cm_user_id=self.username, names=clouds, types=['images'])
            p_format = self.arguments['--format']

            # --column
            # available columns are: id, name, vcpus, ram, disk, refresh time,
            # and all

            if self.arguments['--column']:
                if self.arguments['--column'] != "all":
                    s_column = [x.strip() for x in
                                self.arguments['--column'].split(',')]
                    new_itemkeys = {x: [] for x in itemkeys.keys()}
                    for cloud, items in itemkeys.iteritems():
                        for item in items:
                            if item[0] in s_column:
                                new_itemkeys[cloud].append(item)
                    itemkeys = new_itemkeys

            for cloud in clouds:
                self.cloudmanage.print_cloud_images(username=self.username,
                                                    cloudname=cloud.encode(
                                                        "ascii"),
                                                    itemkeys=itemkeys,
                                                    refresh=False, output=False,
                                                    print_format=p_format)

        else:
            return

    def _list_server(self):
        self.cloudmanage._connect_to_mongo()
        clouds = self.get_working_cloud_name()
        if clouds:
            itemkeys = {"openstack":
                        [
                            ['name', 'name'],
                            ['status', 'status'],
                            ['addresses', 'addresses'],
                            ['id', 'id'],
                            ['flavor', 'flavor', 'id'],
                            ['image', 'image', 'id'],
                            ['user_id', 'cm_user_id'],
                            ['metadata', 'metadata'],
                            ['key_name', 'key_name'],
                            ['created', 'created'],
                            ['cloud', 'cm_cloud']
                        ],
                        "ec2":
                        [
                            ["name", "id"],
                            ["status", "extra", "status"],
                            ["addresses", "public_ips"],
                            ["flavor", "extra", "instance_type"],
                            ['id', 'id'],
                            ['image', 'extra', 'imageId'],
                            ["user_id", 'user_id'],
                            ["metadata", "metadata"],
                            ["key_name", "extra", "key_name"],
                            ["created", "extra", "launch_time"]
                        ],
                        "aws":
                        [
                            ["name", "name"],
                            ["status", "extra", "status"],
                            ["addresses", "public_ips"],
                            ["flavor", "extra", "instance_type"],
                            ['id', 'id'],
                            ['image', 'extra', 'image_id'],
                            ["user_id", "user_id"],
                            ["metadata", "metadata"],
                            ["key_name", "extra", "key_name"],
                            ["created", "extra", "launch_time"]
                        ],
                        "azure":
                        [
                            ['name', 'name'],
                            ['status', 'status'],
                            ['addresses', 'vip'],
                            ['flavor', 'flavor', 'id'],
                            ['id', 'id'],
                            ['image', 'image', 'id'],
                            ['user_id', 'user_id'],
                            ['metadata', 'metadata'],
                            ['key_name', 'key_name'],
                            ['created', 'created'],
                        ]
                        }
                        
            itemkeys_short = {"openstack":
                        [
                            ['name', 'name'],
                            ['status', 'status'],
                            ['addresses', 'addresses'],
                            ['flavor', 'flavor', 'id'],
                            ['image', 'image', 'id']
                        ],
                        "ec2":
                        [
                            ["name", "id"],
                            ["status", "extra", "status"],
                            ["addresses", "public_ips"],
                            ["flavor", "extra", "instance_type"],
                            ['image', 'extra', 'imageId']
                        ],
                        "aws":
                        [
                            ["name", "name"],
                            ["status", "extra", "status"],
                            ["addresses", "public_ips"],
                            ["flavor", "extra", "instance_type"],
                            ['image', 'extra', 'image_id']
                        ],
                        "azure":
                        [
                            ['name', 'name'],
                            ['status', 'status'],
                            ['addresses', 'vip'],
                            ['flavor', 'flavor', 'id'],
                            ['image', 'image', 'id']
                        ]
                        }
            if self.refresh_default_setting or self.arguments['--refresh']:
                self.cloudmanage.mongo.activate(
                    cm_user_id=self.username, names=clouds)
                self.cloudmanage.mongo.refresh(
                    cm_user_id=self.username, names=clouds, types=['servers'])
            p_format = self.arguments['--format']

            # --column
            # available columns are: id, name, vcpus, ram, disk, refresh time,
            # and all

            if self.arguments['--column']:
                if self.arguments['--column'] != "all":
                    s_column = [x.strip() for x in
                                self.arguments['--column'].split(',')]
                    new_itemkeys = {x: [] for x in itemkeys.keys()}
                    for cloud, items in itemkeys.iteritems():
                        for item in items:
                            if item[0] in s_column:
                                new_itemkeys[cloud].append(item)
                    itemkeys = new_itemkeys
            else:
                if not self.arguments['--detail']:
                    itemkeys = itemkeys_short

            for cloud in clouds:
                self.cloudmanage.print_cloud_servers(username=self.username,
                                                     cloudname=cloud.encode(
                                                         "ascii"),
                                                     itemkeys=itemkeys,
                                                     refresh=False,
                                                     output=False,
                                                     print_format=p_format,
                                                     group=self.arguments['--group'])

        else:
            return

    def _list_project(self):
        self.cloudmanage._connect_to_mongo()
        selected_project = None
        try:
            selected_project = self.cloudmanage.mongo.db_defaults.find_one(
                {'cm_user_id': self.username + "OIO"})['project']
        except Exception, NoneType:
            Console.warning("could not find selected project in the database")

        except Exception, e:
            Console.error("could not connect to the database")
            print(e)

        print("\n")
        print(tabulate([[selected_project]], ["selected project"], tablefmt=list_command_table_format))

        #
        # active projects
        #

        projects = {}

        for state in ["active", "completed"]:

            projects[state] = None
            try:
                projects[state] = self.cloudmanage.mongo.db_user.find_one(
                    {'cm_user_id': self.username})['projects'][state]
            except:
                Console.error(
                    "could not find objects or connect to the database containing the projects")

            to_print = []
            if projects[state] is None:
                to_print = [[None]]
            else:
                to_print = [[str(p)] for p in projects[state]]
            print("\n")
            print(tabulate(to_print, ["{0} projects".format(state)], tablefmt=list_command_table_format))

    def _list_cloud(self):
        """ same as the shell_command_cloud list"""
        arguments = dict(self.arguments)
        arguments["list"] = True
        shell_command_cloud(arguments)

        """
        self.cloudmanage._connect_to_mongo()
        active_clouds = []
        other_clouds = []
        activeclouds = self.cloudmanage.mongo.active_clouds(self.username)
        clouds = self.cloudmanage.get_clouds(self.username)
        clouds = clouds.sort([('cm_cloud', 1)])
        for cloud in clouds:
            name = cloud['cm_cloud']
            if name in activeclouds:
                active_clouds.append([str(name)])
            else:
                other_clouds.append([str(name)])
        if active_clouds == []: active_clouds = [None]
        if other_clouds == []: other_clouds = [None]
        print tabulate(active_clouds, ["active clouds"], tablefmt=list_command_table_format)
        print "\n"
        print tabulate(other_clouds, ["other clouds"], tablefmt=list_command_table_format)
        print "\n"
        """

    # --------------------------------------------------------------------------

    def get_working_cloud_name(self):
        '''
        get the name of a cloud to be work on, if CLOUD not given, will pick the
        slected cloud, is --all, will return a list of active clouds
        '''
        self.cloudmanage._connect_to_mongo()
        activeclouds = None
        try:
            activeclouds = self.cloudmanage.mongo.active_clouds(self.username)
        except:
            pass
        if self.arguments['--all']:
            if activeclouds is None:
                print("no active cloud, please activate a cloud by 'cloud on [CLOUD]'")
                return False
            return activeclouds
        else:
            if self.arguments['CLOUD']:
                name = self.arguments['CLOUD']
            else:
                name = self.cloudmanage.get_selected_cloud(self.username)
            if self.cloudmanage.get_clouds(self.username, getone=True, cloudname=name) is None:
                Console.error(
                    "no cloud information of '{0}' in database".format(name))
                return False
            if name not in activeclouds:
                Console.warning(
                    "cloud '{0}' is not active, to activate a cloud: cloud on [CLOUD]".format(name))
                return False
            return [name]

    def execute(self):
        if self.arguments['vm']:
            self._list_server()
        elif self.arguments['flavor']:
            self._list_flavor()
        elif self.arguments['image']:
            self._list_image()
        elif self.arguments['project']:
            self._list_project()
        elif self.arguments['cloud']:
            self._list_cloud()


def main():
    arguments = docopt(shell_command_list.__doc__)
    shell_command_list(arguments)

if __name__ == '__main__':
    main()
