"""Class for managing an OpenEnergyTrackerReader."""

from homeassistant.helpers.device_registry import DeviceInfo


class OpenEnergyTrackerReader:
    """Class for managing an OpenEnergyTrackerReader."""

    def __init__(self, serial : str, identifiers : set[tuple[str, str]]):
        """Initialize."""
        self.serial = serial
        self.data = {}
        self.device_info = None
        self.identifiers = identifiers

    def update(self, new_data : dict):
        """Updates data from the gateway."""
        self.data = new_data

        if self.device_info is None:
            self.device_info = DeviceInfo(identifiers=self.identifiers)

    @property
    def reader_name(self):
        """Returns the name of the reader."""
        return f"Reader {self.data['id']}"

    @property
    def sw_version(self):
        """Returns the software version of the reader."""
        return str(self.data['softver'])

    @property
    def current_power(self):
        """Returns the current_power in watts of the reader."""
        return self.data['power']

    @property
    def battery_voltage(self):
        """Returns the battery_voltage in volts of the reader."""
        return self.data['battery_mV']
