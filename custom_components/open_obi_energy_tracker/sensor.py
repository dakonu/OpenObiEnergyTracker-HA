"""Support for OpenOBI sensors."""

import re
from typing import override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfRatio,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import OpenOBIConfigEntry, OpenOBICoordinator
from .OpenEnergyTrackerReader import OpenEnergyTrackerReader


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenOBIConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
    """Setup components."""

    coordinator : OpenOBICoordinator = entry.runtime_data

    entities : list[SensorEntity] = []
    for reader in coordinator.client.readers.values():
        entities.append(OpenObiSensor(coordinator, 'power', 'reader_power', UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, reader))
        entities.append(OpenObiSensor(coordinator, 'import', 'reader_import', UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL, reader, value_fn=lambda v: float(v)/1000.0))
        entities.append(OpenObiSensor(coordinator, 'battery_mV', 'reader_voltage', UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, reader, value_fn=lambda v: float(v)/1000.0, precision=3))
        entities.append(OpenObiSensor(coordinator, 'battery_mV', 'reader_battery', UnitOfRatio.PERCENTAGE, SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, reader, value_fn=lambda v: max(0,min(100,round((v-2400)/8)))))
        entities.append(OpenObiSensor(coordinator, 'snr', 'reader_snr', SIGNAL_STRENGTH_DECIBELS, SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT, reader))
        entities.append(OpenObiSensor(coordinator, 'rssi', 'reader_rssi', SIGNAL_STRENGTH_DECIBELS_MILLIWATT, SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT, reader))

    async_add_entities(entities, True)


class OpenObiSensor(CoordinatorEntity[OpenOBICoordinator], SensorEntity):
    """Implementation of a open OBI sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator : OpenOBICoordinator,
        reader_field_name: str,
        name_key: str,
        unit: str,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass,
        reader: OpenEnergyTrackerReader,
        **kwargs
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.value_fn = lambda v: v
        self.precision = None
        self.__dict__.update(kwargs)
        self._attr_unique_id = f"{reader.serial}_{name_key}"
        self.entity_id = f"sensor.{re.sub('[^a-z0-9_]+', '_', self._attr_unique_id.lower())}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = reader.device_info
        self.reader_field_name = reader_field_name
        self.reader = reader
        self.entity_description = SensorEntityDescription(key=f"OpenOBIReader_{reader_field_name}", name=name_key, translation_key=name_key, suggested_display_precision=self.precision)

    @property
    @override
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        return self.value_fn(self.reader.data[self.reader_field_name])

    async def async_update(self) -> None:
        """Get the latest data from the device."""
        self._attr_native_value = self.reader.data[self.reader_field_name]

        self.async_write_ha_state()
