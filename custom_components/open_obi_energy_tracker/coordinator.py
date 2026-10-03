"""Define an object to manage fetching OpenOBIEnergyTracker data."""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .OpenEnergyTrackerGateway import OpenEnergyTrackerGateway
from .OpenEnergyTrackerReader import OpenEnergyTrackerReader

type OpenOBIConfigEntry = ConfigEntry[OpenOBICoordinator]


@dataclass
class OpenOBIData:
    """Class for OpenOBIEnergyTracker data."""

    readers: dict[str, OpenEnergyTrackerReader]
    status: dict[str, Any]


class OpenOBICoordinator(DataUpdateCoordinator[OpenOBIData]):
    """Class to manage fetching OpenOBIEnergyTracker data."""

    config_entry: OpenOBIConfigEntry
    current_version: str

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: OpenOBIConfigEntry,
        client: OpenEnergyTrackerGateway,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            config_entry=config_entry,
            name=f"OpenOBIEnergyTracker {client.host}",
            update_interval=SCAN_INTERVAL,
            always_update=True
        )
        self.client = client
        assert self.config_entry.unique_id
        self.serial_number = self.config_entry.unique_id

    @override
    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        # try:
        if await self.client.update():
            device_registry = dr.async_get(self.hass)
            device_registry.async_get_or_create(
                config_entry_id=self.config_entry.entry_id,
                identifiers={(DOMAIN, self.client.serial_number)},
                sw_version=self.client.sw_version,
                name=self.client.gateway_name
                )
            self.current_version = self.client.sw_version
            self.reader_versions = {}

            for uuid,reader in self.client.readers.items():
                device_registry.async_get_or_create(
                    config_entry_id = self.config_entry.entry_id,
                    identifiers = {(DOMAIN, f"{self.client.serial_number}_{uuid}")},
                    name = reader.reader_name,
                    sw_version = reader.sw_version
                )

                self.reader_versions[uuid] = reader.sw_version
        # except OpenOBIError as error:
        #     raise UpdateFailed(
        #         translation_domain=DOMAIN,
        #         translation_key="update_error",
        #         translation_placeholders={"error": str(error)},
        #     ) from error

    @override
    async def _async_update_data(self) -> OpenOBIData:
        # try:
        if await self.client.update():
            readers = self.client.readers
            status = self.client.statusData
        # except error:
        #     raise UpdateFailed(
        #         translation_domain=DOMAIN,
        #         translation_key="update_error",
        #         translation_placeholders={"error": str(error)},
        #     ) from error
        device_registry = dr.async_get(self.hass)

        if self.client.sw_version != self.current_version:
            device_entry = device_registry.async_get_device_by_identifier(
                (DOMAIN, self.serial_number), self.config_entry.entry_id
            )
            assert device_entry
            device_registry.async_update_device(
                device_entry.id,
                sw_version=self.client.sw_version,
            )
            self.current_version = self.client.sw_version

        # Update Readers
        for uuid,reader in self.client.readers.items():
            if self.reader_versions[uuid] != reader.sw_version:
                device_entry = device_registry.async_get_device_by_identifier(
                    (DOMAIN, f"{self.client.serial_number}_{uuid}"), self.config_entry.entry_id
                )
                assert device_entry
                device_registry.async_update_device(
                    device_entry.id,
                    sw_version=reader.sw_version
                )
                self.reader_versions[uuid] = reader.sw_version

        return OpenOBIData(readers, status)
