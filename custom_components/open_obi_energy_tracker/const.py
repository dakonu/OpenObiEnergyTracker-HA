"""Constants for the Open OBI Energy Tracker integration."""

from datetime import timedelta
import logging

SCAN_INTERVAL = timedelta(seconds=30)

DOMAIN = "open_obi_energy_tracker"

LOGGER = logging.getLogger(__package__)
