"""Class for managing OpenEnergyTrackerGateway."""
import json

import aiohttp

from .const import DOMAIN
from .OpenEnergyTrackerReader import OpenEnergyTrackerReader


class OpenEnergyTrackerGateway:
    """Class for managing OpenEnergyTrackerGateway."""

    def __init__(self, host: str, session : aiohttp.ClientSession) -> None:
        """Initialize."""
        self.host = host
        self.session = session or aiohttp.ClientSession()
        self.statusData = None
        self.readers : dict[str, OpenEnergyTrackerReader] = {}

    async def update(self) -> bool:
        """Updates data from the gateway."""

        async with self.session.get(f'http://{self.host}/api/status') as response:
            if response.status != 200:
                return False

            self.statusData = json.loads(await response.text())

        async with self.session.get(f'http://{self.host}/api/readers') as response:
            if response.status != 200:
                return False

            readersdata = json.loads(await response.text())

            for reader in readersdata:
                if reader['uuid'] not in self.readers:
                    self.readers[reader['uuid']] = OpenEnergyTrackerReader(reader['uuid'], {(DOMAIN, f"{self.serial_number}_{reader['uuid']}")})

                self.readers[reader['uuid']].update(reader)

            # Delete readers which are not present
            currentids = [r['uuid'] for r in readersdata]
            for r in self.readers:
                if r not in currentids:
                    del self.readers[r]

        return True

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True

    @property
    def gateway_name(self):
        """Returns the name of the gateway."""
        return self.statusData['gw_custom_name'] or f"OBI Gateway {self.statusData['gw']}"

    @property
    def sw_version(self):
        """Returns the software version of the gateway."""
        return self.statusData['fw']['version']

    @property
    def serial_number(self):
        """Returns the serial number of the gateway."""
        return self.statusData['mac']
