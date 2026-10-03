# OpenObiEnergyTracker-HA
Homeassistant integration for OBI Energy-Tracker with custom firmware.

It doesn't work with the stock firmware. You need to install the cloud-free firmware from [atc1441](https://github.com/atc1441/OBI_Energy_Tracker_Local_Cloud/tree/main)


## Installation

### HACS (Recommended)

1. In HACS, go to **Integrations** → **⋮** → **Custom repositories**
2. Add repository: `https://github.com/dakonu/OpenObiEnergyTracker-HA`
3. Category: **Integration**
4. Click **Add**
5. Search for "Open OBI-Energy-Tracker" in HACS
6. Click **Install**
7. Restart Home Assistant
8. Go to Settings > Devices & Services > Add Integration
9. Search for "Open OBI-Energy-Tracker" and follow the setup wizard

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/open_obi_energy_tracker` directory to your Home Assistant `config/custom_components` folder
3. Restart Home Assistant
4. Go to Settings > Devices & Services > Add Integration
5. Search for "Open OBI-Energy-Tracker" and complete the configuration
