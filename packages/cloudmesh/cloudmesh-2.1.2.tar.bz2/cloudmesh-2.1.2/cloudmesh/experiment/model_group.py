#
# terminal 1: fab manage.mongo
# terminal 2: python model_group.py
#
from __future__ import print_function
from mongoengine import StringField, Document
from cloudmesh_common.tables import array_dict_table_printer
import json
from cloudmesh.config.cm_config import get_mongo_db, get_mongo_dbname_from_collection, DBConnFactory


class ExperimentBase(Document):
    cm_kind = StringField(default="experiment")
    cm_label = StringField()
    cm_userid = StringField()
    dbname = get_mongo_dbname_from_collection("experiment")
    if dbname:
        meta = {'allow_inheritance': True, 'db_alias': dbname}
    else:
        meta = {'allow_inheritance': True}


class ExperimentVM(ExperimentBase):
    cloud = StringField()
    vmid = StringField()


class ExperimentGroup(object):
    
    def __init__(self, userid, label):

        self.userid = userid
        self.label = label
        get_mongo_db("experiment", DBConnFactory.TYPE_MONGOENGINE)

    def add(self, vm):
        vm.cm_label = self.label
        vm.cm_userid = self.userid
        vm.save()

    def get(self, label=None):
        if label is None:
            label = self.label
        # ide was, but does not work, so we use solution by hardcoding
        # args = ExperimentVM._fields
        # vms = ExperimentVM.objects(userid=self.userid,
        #                            label=self.label).only(*args)
        if label in ["all"]:
            vms = ExperimentVM.objects(cm_userid=self.userid).only(
                'cm_userid',
                'cm_label',
                'cloud',
                'vmid')
        else:
            vms = ExperimentVM.objects(
                cm_userid=self.userid,
                cm_label=label).only('cm_userid',
                                     'cm_label',
                                     'cloud',
                                     'vmid')

        return json.loads(vms.to_json())

    def delete(self, label):
        vms = ExperimentVM.objects(cm_userid=self.userid,
                                   cm_label=self.label)
        for vm in vms:
            vm.delete()

    def to_table(self, label):
        data = self.get(label)
        if data == []:
            return "No data found"
        else:
            return array_dict_table_printer(data)


def main():
    username = "fuwang"
    label = "exp-a"

    experiment = ExperimentGroup(username, label)

    experiment.delete(label)

    for i in range(1, 10):
        vm = ExperimentVM(
            cm_label=label,
            cm_userid=username,
            cloud="india",
            vmid="myid-{0}".format(i),
        )
        experiment.add(vm)

    vms = ExperimentVM.objects()
    for vm in vms:
        print(vm.cm_label, vm.cm_userid, vm.vmid, vm.cloud)

    print(experiment.to_table(label))


if __name__ == "__main__":
    main()
