from twisted.internet import defer
from nav.mibs import mibretriever
from nav.mibs.dlink_equipment_mib import DlinkEquipmentMib
from nav.mibs.dlink_ddm_mib import DlinkDdmMib

class DlinkSensorsMib(mibretriever.MibRetriever):

    def __init__(self, agent):
        super(DlinkSensorsMib, self).__init__(agent)
        self.dlink_equipment_mib = DlinkEquipmentMib(agent)
        self.dlink_ddm_mib = DlinkDdmMib(agent)

    @defer.inlineCallbacks
    def get_all_sensors(self):
        equipment_sensors = yield self.dlink_equipment_mib.get_all_sensors()
        ddm_sensors = yield self.dlink_ddm_mib.get_all_sensors()
        result = equipment_sensors + ddm_sensors
        defer.returnValue(result)
