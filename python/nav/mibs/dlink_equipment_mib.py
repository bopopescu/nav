from twisted.internet import defer
from nav.mibs import reduce_index
from nav.mibs import mibretriever


class DlinkEquipmentMib(mibretriever.MibRetriever):
    def get_module_name(self):
        return self.mib.get('moduleName', None)

    def _get_temperature_sensors(self):
        df = self.retrieve_columns([
            'swTemperatureUnitIndex',
            'swTemperatureCurrent',
        ])
        df.addCallback(reduce_index)
        return df

    def _get_temperature_sensor_params(self, sensors):
        result = []
        for idx, sensor in sensors.items():
            sensor_oid = sensor.get(0, None)

            mib = self.nodes.get('swTemperatureCurrent', None)
            oid = str(mib.oid) + str(sensor_oid)
            name = 'swTemperatureCurrent ' + str(sensor.get('swTemperatureUnitIndex'))
            result.append({
                'oid': oid,
                'unit_of_measurement': 'Celsius',
                'precision': 0,
                'scale': None,
                'description': name,
                'name': name,
                'internal_name': name,
                'mib': self.get_module_name(),
            })
        return result

    def _get_fan_speed_sensors(self):
        df = self.retrieve_columns([
            'swFanID',
            'swFanUnitIndex',
            'swFanSpeed',
        ])
        df.addCallback(reduce_index)
        return df

    def _get_fan_speed_sensor_params(self, sensors):
        result = []
        for idx, sensor in sensors.items():
            sensor_oid = sensor.get(0, None)

            mib = self.nodes.get('swFanSpeed', None)
            oid = str(mib.oid) + str(sensor_oid)
            name = 'swFanSpeed ' + str(sensor.get('swFanUnitIndex')) + '/' + str(sensor.get('swFanID'))
            result.append({
                'oid': oid,
                'unit_of_measurement': 'RPM',
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
        temperature_sensors = yield self._get_temperature_sensors()
        fan_speed_sensors = yield self._get_fan_speed_sensors()
        result = self._get_temperature_sensor_params(temperature_sensors)
        result.extend(self._get_fan_speed_sensor_params(fan_speed_sensors))
        defer.returnValue(result)
