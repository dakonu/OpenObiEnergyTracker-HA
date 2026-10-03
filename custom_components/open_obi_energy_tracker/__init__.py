"""The Open OBI Energy Tracker integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import OpenOBICoordinator
from .OpenEnergyTrackerGateway import OpenEnergyTrackerGateway

PLATFORMS: list[Platform] = [
    # Platform.BUTTON,
    #Platform.NUMBER,
    #Platform.SELECT,
    Platform.SENSOR,
    #Platform.SWITCH,
    # Platform.UPDATE,
]

type OpenOETApi = ConfigEntry[OpenEnergyTrackerGateway]

async def async_setup_entry(hass: HomeAssistant, entry: OpenOETApi) -> bool:
    """Set up OpenObiEnergyTracker from a config entry."""

    client = OpenEnergyTrackerGateway(
        entry.data[CONF_HOST], session=async_get_clientsession(hass)
    )

    coordinator = OpenOBICoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: OpenOETApi
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
