# garth-mcp-server

[![PyPI version](
    https://img.shields.io/pypi/v/garth-mcp-server.svg?logo=python&logoColor=brightgreen&color=brightgreen)](
    https://pypi.org/project/garth-mcp-server/)

Garmin Connect MCP server based on [garth](https://github.com/matin/garth).

## Usage

![image](https://github.com/user-attachments/assets/14221e6f-5f65-4c21-bc7a-2147c1c9efc1)

## Install

```json
{
  "mcpServers": {
    "Garth - Garmin Connect": {
      "command": "uvx",
      "args": [
        "garth-mcp-server"
      ],
      "env": {
        "GARTH_TOKEN": "<output of `uvx garth login`>"
      }
    }
  }
}
```

Make sure the path for the `uvx` command is fully scoped as MCP doesn't
use the same PATH your shell does. On macOS, it's typically
`/Users/{user}/.local/bin/uvx`.

## Tools

### Health & Wellness (using Garth data classes)

- `user_profile` - Get user profile information
- `user_settings` - Get user settings and preferences
- `nightly_sleep` - Get detailed sleep data with optional movement data
- `daily_sleep` - Get daily sleep summary data
- `daily_stress` / `weekly_stress` - Get stress data
- `daily_intensity_minutes` / `weekly_intensity_minutes` - Get intensity minutes
- `daily_body_battery` - Get body battery data
- `daily_hydration` - Get hydration data
- `daily_steps` / `weekly_steps` - Get steps data
- `daily_hrv` / `hrv_data` - Get heart rate variability data

### Activities (using Garmin Connect API)

- `get_activities` - Get list of activities with optional filters
- `get_activities_by_date` - Get activities for a specific date
- `get_activity_details` - Get detailed activity information
- `get_activity_splits` - Get activity lap/split data
- `get_activity_weather` - Get weather data for activities

### Additional Health Data (using Garmin Connect API)

- `get_body_composition` - Get body composition data
- `get_respiration_data` - Get respiration data
- `get_spo2_data` - Get SpO2 (blood oxygen) data
- `get_blood_pressure` - Get blood pressure readings

### Device & Gear (using Garmin Connect API)

- `get_devices` - Get connected devices
- `get_device_settings` - Get device settings
- `get_gear` - Get gear information
- `get_gear_stats` - Get gear usage statistics

### Utility Tools

- `monthly_activity_summary` - Get monthly activity overview
- `snapshot` - Get snapshot data for date ranges
- `get_connectapi_endpoint` - Direct access to any Garmin Connect API endpoint
