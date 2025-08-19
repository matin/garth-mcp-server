import os
from datetime import date
from functools import wraps
from urllib.parse import urlencode

import garth
from mcp.server.fastmcp import FastMCP


__version__ = "0.0.8"

server = FastMCP("Garth - Garmin Connect", dependencies=["garth"])


def requires_garth_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = os.getenv("GARTH_TOKEN")
        if not token:
            return "You must set the GARTH_TOKEN environment variable to use this tool"
        garth.client.loads(token)
        return func(*args, **kwargs)

    return wrapper


# Tools using Garth data classes


@server.tool()
@requires_garth_session
def user_profile() -> str | garth.UserProfile:
    """
    Get user profile information using Garth's UserProfile data class.
    """
    return garth.UserProfile.get()


@server.tool()
@requires_garth_session
def user_settings() -> str | garth.UserSettings:
    """
    Get user settings using Garth's UserSettings data class.
    """
    return garth.UserSettings.get()


@server.tool()
@requires_garth_session
def weekly_intensity_minutes(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyIntensityMinutes]:
    """
    Get weekly intensity minutes data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklyIntensityMinutes.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_body_battery(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyBodyBatteryStress]:
    """
    Get daily body battery data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyBodyBatteryStress.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_hydration(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHydration]:
    """
    Get daily hydration data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyHydration.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_steps(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySteps]:
    """
    Get daily steps data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailySteps.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_steps(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklySteps]:
    """
    Get weekly steps data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklySteps.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_hrv(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHRV]:
    """
    Get daily heart rate variability data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyHRV.list(end_date, days)


@server.tool()
@requires_garth_session
def hrv_data(end_date: date | None = None, days: int = 1) -> str | list[garth.HRVData]:
    """
    Get detailed HRV data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.HRVData.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_sleep(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySleep]:
    """
    Get daily sleep summary data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailySleep.list(end_date, days)


# Tools using direct API calls


@server.tool()
@requires_garth_session
def get_activities(
    start_date: str | None = None, limit: int | None = None
) -> str | dict | None:
    """
    Get list of activities from Garmin Connect.
    start_date: Start date for activities (YYYY-MM-DD format)
    limit: Maximum number of activities to return
    """
    params = {}
    if start_date:
        params["startDate"] = start_date
    if limit:
        params["limit"] = str(limit)

    endpoint = "activitylist-service/activities/search/activities"
    if params:
        endpoint += "?" + urlencode(params)
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def get_activities_by_date(date: str) -> str | dict | None:
    """
    Get activities for a specific date from Garmin Connect.
    date: Date for activities (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailySummaryChart/{date}")


@server.tool()
@requires_garth_session
def get_activity_details(activity_id: str) -> str | dict | None:
    """
    Get detailed information for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}")


@server.tool()
@requires_garth_session
def get_activity_splits(activity_id: str) -> str | dict | None:
    """
    Get lap/split data for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/splits")


@server.tool()
@requires_garth_session
def get_activity_weather(activity_id: str) -> str | dict | None:
    """
    Get weather data for a specific activity.
    activity_id: Garmin Connect activity ID
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/weather")


@server.tool()
@requires_garth_session
def get_body_composition(date: str | None = None) -> str | dict | None:
    """
    Get body composition data from Garmin Connect.
    date: Date for body composition data (YYYY-MM-DD format), if not provided returns latest
    """
    if date:
        endpoint = f"wellness-service/wellness/bodyComposition/{date}"
    else:
        endpoint = "wellness-service/wellness/bodyComposition"
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def get_respiration_data(date: str) -> str | dict | None:
    """
    Get respiration data from Garmin Connect.
    date: Date for respiration data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyRespiration/{date}")


@server.tool()
@requires_garth_session
def get_spo2_data(date: str) -> str | dict | None:
    """
    Get SpO2 (blood oxygen) data from Garmin Connect.
    date: Date for SpO2 data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyPulseOx/{date}")


@server.tool()
@requires_garth_session
def get_blood_pressure(date: str) -> str | dict | None:
    """
    Get blood pressure readings from Garmin Connect.
    date: Date for blood pressure data (YYYY-MM-DD format)
    """
    return garth.connectapi(f"wellness-service/wellness/dailyBloodPressure/{date}")


@server.tool()
@requires_garth_session
def get_devices() -> str | dict | None:
    """
    Get connected devices from Garmin Connect.
    """
    return garth.connectapi("device-service/deviceregistration/devices")


@server.tool()
@requires_garth_session
def get_device_settings(device_id: str) -> str | dict | None:
    """
    Get settings for a specific device.
    device_id: Device ID from Garmin Connect
    """
    return garth.connectapi(
        f"device-service/deviceservice/device-info/settings/{device_id}"
    )


@server.tool()
@requires_garth_session
def get_gear() -> str | dict | None:
    """
    Get gear information from Garmin Connect.
    """
    return garth.connectapi("gear-service/gear")


@server.tool()
@requires_garth_session
def get_gear_stats(gear_uuid: str) -> str | dict | None:
    """
    Get usage statistics for specific gear.
    gear_uuid: UUID of the gear item
    """
    return garth.connectapi(f"gear-service/gear/stats/{gear_uuid}")


@server.tool()
@requires_garth_session
def get_connectapi_endpoint(endpoint: str) -> str | dict | None:
    """
    Get the data from a given Garmin Connect API endpoint.
    This is a generic tool that can be used to get data from any Garmin Connect API endpoint.
    """
    return garth.connectapi(endpoint)


@server.tool()
@requires_garth_session
def nightly_sleep(
    end_date: date | None = None, nights: int = 1, sleep_movement: bool = False
) -> str | list[garth.SleepData]:
    """
    Get sleep stats for a given date and number of nights.
    If no date is provided, the current date will be used.
    If no nights are provided, 1 night will be used.
    sleep_movement provides detailed sleep movement data. If looking at
    multiple nights, it'll be a lot of data.
    """
    sleep_data = garth.SleepData.list(end_date, nights)
    if not sleep_movement:
        for night in sleep_data:
            if hasattr(night, "sleep_movement"):
                del night.sleep_movement
    return sleep_data


@server.tool()
@requires_garth_session
def daily_stress(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyStress]:
    """
    Get daily stress data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyStress.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_stress(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyStress]:
    """
    Get weekly stress data for a given date and number of weeks.
    If no date is provided, the current date will be used.
    If no weeks are provided, 1 week will be used.
    """
    return garth.WeeklyStress.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_intensity_minutes(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyIntensityMinutes]:
    """
    Get daily intensity minutes data for a given date and number of days.
    If no date is provided, the current date will be used.
    If no days are provided, 1 day will be used.
    """
    return garth.DailyIntensityMinutes.list(end_date, days)


@server.tool()
@requires_garth_session
def monthly_activity_summary(month: int, year: int) -> str | dict | None:
    """
    Get the monthly activity summary for a given month and year.
    """
    return garth.connectapi(f"mobile-gateway/calendar/year/{year}/month/{month}")


@server.tool()
@requires_garth_session
def snapshot(from_date: date, to_date: date) -> str | dict | None:
    """
    Get the snapshot for a given date range. This is a good starting point for
    getting data for a given date range. It can be used in combination with
    the get_connectapi_endpoint tool to get data from any Garmin Connect API
    endpoint.
    """
    return garth.connectapi(f"mobile-gateway/snapshot/detail/v2/{from_date}/{to_date}")


def main():
    server.run()


if __name__ == "__main__":
    main()
