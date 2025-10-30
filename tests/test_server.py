import json
import pytest
from fastmcp.client import Client
import garth

@pytest.mark.vcr
async def test_list_tools(mcp_client: Client):
    list_tools = await mcp_client.list_tools()
    assert len(list_tools) > 0

# Garth data class tools
@pytest.mark.vcr
async def test_user_profile(mcp_client: Client):
    response = await mcp_client.call_tool("user_profile")
    assert response.is_error is False
    assert response.content[0].type == "text"
    profile_data = json.loads(response.content[0].text)
    assert garth.UserProfile(**profile_data)

@pytest.mark.vcr
async def test_user_settings(mcp_client: Client):
    response = await mcp_client.call_tool("user_settings")
    assert response.is_error is False
    assert response.content[0].type == "text"
    settings_data = json.loads(response.content[0].text)
    assert garth.UserSettings(**settings_data)

@pytest.mark.vcr
async def test_weekly_intensity_minutes(mcp_client: Client):
    response = await mcp_client.call_tool("weekly_intensity_minutes")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.WeeklyIntensityMinutes(**data)

@pytest.mark.vcr
async def test_daily_body_battery(mcp_client: Client):
    response = await mcp_client.call_tool("daily_body_battery")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailyBodyBatteryStress(**data)

@pytest.mark.vcr
async def test_daily_hydration(mcp_client: Client):
    response = await mcp_client.call_tool("daily_hydration", {"days": 100})
    assert response.is_error is False
    # No data returned for daily hydration
    assert response.data.result == []

@pytest.mark.vcr
async def test_daily_steps(mcp_client: Client):
    response = await mcp_client.call_tool("daily_steps")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailySteps(**data)

@pytest.mark.vcr
async def test_weekly_steps(mcp_client: Client):
    response = await mcp_client.call_tool("weekly_steps")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.WeeklySteps(**data)

@pytest.mark.vcr
async def test_daily_hrv(mcp_client: Client):
    response = await mcp_client.call_tool("daily_hrv")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailyHRV(**data)

@pytest.mark.vcr
async def test_hrv_data(mcp_client: Client):
    response = await mcp_client.call_tool("hrv_data")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.HRVData(**data)

@pytest.mark.vcr
async def test_daily_sleep(mcp_client: Client):
    response = await mcp_client.call_tool("daily_sleep")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailySleep(**data)

@pytest.mark.vcr
async def test_nightly_sleep(mcp_client: Client):
    response = await mcp_client.call_tool("nightly_sleep")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.SleepData(**data)

@pytest.mark.vcr
async def test_daily_stress(mcp_client: Client):
    response = await mcp_client.call_tool("daily_stress")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailyStress(**data)

@pytest.mark.vcr
async def test_weekly_stress(mcp_client: Client):
    response = await mcp_client.call_tool("weekly_stress")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.WeeklyStress(**data)

@pytest.mark.vcr
async def test_daily_intensity_minutes(mcp_client: Client):
    response = await mcp_client.call_tool("daily_intensity_minutes")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)
    assert garth.DailyIntensityMinutes(**data)

# ConnectAPI tools
@pytest.mark.vcr
async def test_get_activities(mcp_client: Client):
    response = await mcp_client.call_tool("get_activities")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)

@pytest.mark.vcr
async def test_get_activities_by_date(mcp_client: Client):
    response = await mcp_client.call_tool("get_activities_by_date", {"date": "2024-01-15"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_activity_related_tools(mcp_client: Client):
    # First get activities to find a real activity ID
    activities_response = await mcp_client.call_tool("get_activities")
    assert activities_response.is_error is False
    activities_data = json.loads(activities_response.content[0].text)

    # Get the first activity ID
    activity_id = str(activities_data.get("activityId"))
    assert activity_id != "None"

    # Test activity details with real ID
    details_response = await mcp_client.call_tool("get_activity_details", {"activity_id": activity_id})
    assert details_response.is_error is False
    assert details_response.content[0].type == "text"
    details_data = json.loads(details_response.content[0].text)
    assert isinstance(details_data, dict)

    # Test activity splits with real ID
    splits_response = await mcp_client.call_tool("get_activity_splits", {"activity_id": activity_id})
    assert splits_response.is_error is False
    assert splits_response.content[0].type == "text"
    splits_data = json.loads(splits_response.content[0].text)
    assert isinstance(splits_data, (dict, list))

    # Test activity weather with real ID
    weather_response = await mcp_client.call_tool("get_activity_weather", {"activity_id": activity_id})
    assert weather_response.is_error is False
    assert weather_response.content[0].type == "text"
    weather_data = json.loads(weather_response.content[0].text)
    assert isinstance(weather_data, dict)


@pytest.mark.vcr
async def test_get_respiration_data(mcp_client: Client):
    response = await mcp_client.call_tool("get_respiration_data", {"date": "2025-10-29"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_get_spo2_data(mcp_client: Client):
    response = await mcp_client.call_tool("get_spo2_data", {"date": "2024-01-15"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_get_blood_pressure(mcp_client: Client):
    response = await mcp_client.call_tool("get_blood_pressure", {"date": "2025-10-29"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_get_devices(mcp_client: Client):
    response = await mcp_client.call_tool("get_devices")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_get_device_settings(mcp_client: Client):
    response = await mcp_client.call_tool("get_device_settings", {"device_id": "123456789"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, dict)

@pytest.mark.vcr
async def test_get_gear(mcp_client: Client):
    response = await mcp_client.call_tool("get_gear")
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))


@pytest.mark.vcr
async def test_monthly_activity_summary(mcp_client: Client):
    response = await mcp_client.call_tool("monthly_activity_summary", {"month": 1, "year": 2024})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))

@pytest.mark.vcr
async def test_snapshot(mcp_client: Client):
    response = await mcp_client.call_tool("snapshot", {"from_date": "2024-01-01", "to_date": "2024-01-31"})
    assert response.is_error is False
    assert response.content[0].type == "text"
    data = json.loads(response.content[0].text)
    assert isinstance(data, (dict, list))
