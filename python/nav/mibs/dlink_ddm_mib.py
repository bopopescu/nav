from twisted.internet import defer
from nav.mibs import reduce_index
from nav.mibs import mibretriever


class DlinkDdmMib(mibretriever.MibRetriever):
    from nav.smidumps.dlink_ddm_mib import MIB as mib

    def get_module_name(self):
        return self.mib.get('moduleName', None)

    def _get_ddm_sensors(self):
        df = self.retrieve_columns([
            'swDdmPort',
            'swDdmPortState',
            'swDdmRxPower',
            'swDdmTxPower',
            'swDdmVoltage',
            'swDdmTemperature',
            'swDdmBiasCurrent',
        ])
        df.addCallback(reduce_index)
        return df

    def _get_ddm_sensor_params(self, sensors):
        result = []
        for idx, sensor in sensors.items():
            if sensor.get('swDdmPortState', None) == 1:
                sensor_oid = sensor.get(0, None)

                mibobject = self.nodes.get('swDdmRxPower', None)
                oid = str(mibobject.oid) + str(sensor_oid)
                name = 'swDdmRxPower ' + str(sensor.get('swDdmPort'))
                result.append({
                    'oid': oid,
                    'unit_of_measurement': 'dBm',
                    'precision': 0,
                    'scale': None,
                    'description': name,
                    'name': name,
                    'internal_name': name,
                    'mib': self.get_module_name(),
                })

                mibobject = self.nodes.get('swDdmTxPower', None)
                oid = str(mibobject.oid) + str(sensor_oid)
                name = 'swDdmTxPower ' + str(sensor.get('swDdmPort'))
                result.append({
                    'oid': oid,
                    'unit_of_measurement': 'dBm',
                    'precision': 0,
                    'scale': None,
                    'description': name,
                    'name': name,
                    'internal_name': name,
                    'mib': self.get_module_name(),
                })

                mibobject = self.nodes.get('swDdmVoltage', None)
                oid = str(mibobject.oid) + str(sensor_oid)
                name = 'swDdmVoltage ' + str(sensor.get('swDdmPort'))
                result.append({
                    'oid': oid,
                    'unit_of_measurement': 'Volts',
                    'precision': 0,
                    'scale': None,
                    'description': name,
                    'name': name,
                    'internal_name': name,
                    'mib': self.get_module_name(),
                })

                mibobject = self.nodes.get('swDdmTemperature', None)
                oid = str(mibobject.oid) + str(sensor_oid)
                name = 'swDdmTemperature ' + str(sensor.get('swDdmPort'))
                result.append({
                    'oid': oid,
                    'unit_of_measurement': 'Celcius',
                    'precision': 0,
                    'scale': None,
                    'description': name,
                    'name': name,
                    'internal_name': name,
                    'mib': self.get_module_name(),
                })

                mibobject = self.nodes.get('swDdmBiasCurrent', None)
                oid = str(mibobject.oid) + str(sensor_oid)
                name = 'swDdmBiasCurrent ' + str(sensor.get('swDdmPort'))
                result.append({
                    'oid': oid,
                    'unit_of_measurement': 'mA',
                    'precision': 0,
                    'scale': None,
                    'description': name,
                    'name': name,
                    'internal_name': name,
                    'mib': self.get_module_name(),
                })
        return result

    @defer.inlineCallbacks
    def get_all_sensors(self):
        ddm_sensors = yield self._get_ddm_sensors()
        result = self._get_ddm_sensor_params(ddm_sensors)
        defer.returnValue(result)
