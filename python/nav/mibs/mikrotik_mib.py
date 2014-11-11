from twisted.internet import defer
from nav.mibs import mibretriever


class MikrotikMib(mibretriever.MibRetriever):
    from nav.smidumps.mikrotik_mib import MIB as mib

    def get_module_name(self):
        return self.mib.get('moduleName', None)

    def _get_temperature_sensor_params(self):
        sensors = []

        mibobject = self.nodes.get('mtxrHlTemperature', None)
        oid = str(mibobject.oid) + '.0'
        name = 'mtxrHlTemperature'
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

        mibobject = self.nodes.get('mtxrHlProcessorTemperature', None)
        oid = str(mibobject.oid) + '.0'
        name = 'mtxrHlProcessorTemperature'
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
        result = yield self._get_temperature_sensor_params()
        defer.returnValue(result)
