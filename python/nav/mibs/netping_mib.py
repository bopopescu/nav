from twisted.internet import defer
from nav.mibs import mibretriever


class NetpingMib(mibretriever.MibRetriever):
    def get_module_name(self):
        return self.mib.get('moduleName', None)

    def _get_thermo_sensor_params(self):
        sensors = []
        for idx in range(1, 9):
            mib = self.nodes.get('npThermoValue', None)
            oid = str(mib.oid) + '.' + str(idx)
            name = 'npThermoValue ' + str(idx)
            sensors.append({
                'oid': oid,
                'unit_of_measurement': 'Celsius',
                'precision': 0,
                'scale': None,
                'description': name,
                'name': name,
                'internal_name': name,
                'mib': self.get_module_name(),
            })
        return sensors

    @defer.inlineCallbacks
    def get_all_sensors(self):
        result = yield self._get_thermo_sensor_params()
        defer.returnValue(result)
