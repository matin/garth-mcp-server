import os
from datetime import date
from functools import wraps
from typing import Any
from urllib.parse import urlencode

import garth
from mcp.server.fastmcp import FastMCP


__version__ = "0.0.10.dev5"

# Type alias for functions that return data from garth.connectapi
ConnectAPIResponse = str | dict | list | int | float | bool | None

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
def user_profile() -> dict[str, Any]:
    """
    Retrieve the authenticated user's Garmin Connect profile.

    Behavior
    - Returns the same structure as Garth's UserProfile data class, serialized to JSON.
    - No parameters are required.
    - Requires an authenticated Garth session. If GARTH_TOKEN is not set, returns a helpful error string instead of JSON.

    Typical fields you can expect (not exhaustive and may vary):
    - profileId, displayName, fullName, userName, location
    - profileImageUrlSmall/Medium/Large
    - profileVisibility and various per-field visibility flags (e.g., showAge, showWeight, showHeight)
    - userRoles (authorization scopes/roles); generally not needed for end-user display

    Good uses for an agent
    - Show the user's display name and basic profile metadata.
    - Decide which profile attributes are safe to surface based on visibility flags.
    - Derive user-specific identifiers (e.g., profileId) needed by other tools.

    Notes
    - Treat image URLs and role/scope fields as optional; they may be absent or not useful for your task.
    - Respect privacy flags (e.g., showAge == false → avoid surfacing age-related details).
    - Age is not returned directly; if a birth date is available and allowed by visibility flags, compute age from it.

    Output format
    - Returns JSON (as text content in MCP) matching Garth's UserProfile shape.
    - The following is just an example of a human-friendly summary you might render from that JSON; it is not the raw return value.

    Example summary (agent-friendly rendering)
    - Name: Test User
    - Age: 39 years (Born on October 17, 1984)
    - Gender: Male
    - Weight: 60 kg
    - Height: 162 cm
    - Location: Ciudad de México, CDMX

    - Profile Image: https://s3.amazonaws.com/garmin-connect-prod/profile_images/73240e81-6e4d-43fc-8af8-c8f6c51b3b8f-2591602.png
    """
    user_profile = garth.UserProfile.get()
    user_setting = garth.UserSettings.get()

    return {
        "id": user_profile.id,
        "profile_id": user_profile.profile_id,
        "display_name": user_profile.display_name,
        "full_name": user_profile.full_name,
        "user_name": user_profile.user_name,
        "user_profile_full_name": user_profile.user_profile_full_name,
        "favorite_activity_types": user_profile.favorite_activity_types,
        "gender": user_setting.user_data.gender,
        "weight": user_setting.user_data.weight,
        "height": user_setting.user_data.height,
        "birth_date": user_setting.user_data.birth_date,
        "measurement_system": user_setting.user_data.measurement_system,
        "activity_level": user_setting.user_data.activity_level,
        "handedness": user_setting.user_data.handedness,
        "power_format": user_setting.user_data.power_format,
        "heart_rate_format": user_setting.user_data.heart_rate_format,
        "first_day_of_week": user_setting.user_data.first_day_of_week,
        "vo_2_max_running": user_setting.user_data.vo_2_max_running,
        "vo_2_max_cycling": user_setting.user_data.vo_2_max_cycling,
        "lactate_threshold_speed": user_setting.user_data.lactate_threshold_speed,
        "lactate_threshold_heart_rate": user_setting.user_data.lactate_threshold_heart_rate,
        "dive_number": user_setting.user_data.dive_number,
        "intensity_minutes_calc_method": user_setting.user_data.intensity_minutes_calc_method,
        "moderate_intensity_minutes_hr_zone": user_setting.user_data.moderate_intensity_minutes_hr_zone,
        "vigorous_intensity_minutes_hr_zone": user_setting.user_data.vigorous_intensity_minutes_hr_zone,
    }


@server.tool()
@requires_garth_session
def user_profile_statistics() -> dict[str, Any]:
    """
    General user statistics and experience summary.

    Retrieves aggregate statistics from Garmin Connect to provide an overview of the user's activity totals across different time periods.

    Behavior
    - Returns a JSON object with aggregated activity statistics:
        - `last_12_months`: Total activity metrics for the previous 12 months including total activities, distance (meters and kilometers), duration (seconds and hours), calories, and elevation gain.
        - `lifetime_totals`: Contains two sub-objects:
            - `activities`: Current year totals (same structure as last_12_months).
            - `lifetime_totals`: All-time aggregated statistics including total steps, distance, calories, goals met in days, active days, wellness distance, and step calories.
    - All distance values are provided in meters, with kilometer conversions added when distance >= 1000m.
    - All duration values are provided in seconds, with hour conversions added when duration >= 3600s.

    Intended Use for Agents
    - Show a comprehensive overview of user activity levels and lifetime achievements, useful for context in health & activity coaching, summaries, introductions, or progress tracking.
    - Allows comparison of user activity levels across different time periods (current year vs last 12 months vs lifetime).
    - Useful for understanding long-term trends and overall fitness engagement.

    Notes
    - Statistics are aggregated across all activity types (not broken down by sport).
    - Personal records (best performances) are not included—use activity-specific tools for detailed records.
    - Returned fields may vary based on available data; treat zeroes/absences as unavailable.
    - Always respect user privacy—do not surface sensitive fields unless relevant to the requested context.

    Output Example:
    {
        "last_12_months": {
            "total_activities": 124,
            "total_distance": 1250000,
            "total_distance_km": 1250.0,
            "total_duration": 72000,
            "total_duration_hours": 20.0,
            "total_calories": 85000,
            "total_elevation_gain": 45000
        },
        "lifetime_totals": {
            "activities": {
                "total_activities": 45,
                "total_distance": 450000,
                "total_distance_km": 450.0,
                "total_duration": 27000,
                "total_duration_hours": 7.5,
                "total_calories": 32000,
                "total_elevation_gain": 15000
            },
            "lifetime_totals": {
                "total_distance": 5432100,
                "total_distance_km": 5432.1,
                "total_steps": 54730927,
                "total_calories": 1250000,
                "total_goals_met_in_days": 234,
                "total_active_days": 456,
                "total_wellness_distance": 1234000,
                "total_wellness_distance_km": 1234.0,
                "total_step_calories": 890000
            }
        }
    }

    """
    # Gather summaries for the last 12 months
    user_profile = garth.UserProfile.get()
    display_name = user_profile.display_name

    # Get user statistics for last 12 months
    data = garth.connectapi(f"userstats-service/statistics/{display_name}")
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    metrics = data["userMetrics"][0]
    activities = {
        "total_activities": metrics["totalActivities"],
        "total_distance": metrics["totalDistance"],
        "total_duration": metrics["totalDuration"],
        "total_calories": metrics["totalCalories"],
        "total_elevation_gain": metrics["totalElevationGain"],
    }
    if activities["total_distance"] >= 1000:
        activities["total_distance_km"] = round(activities["total_distance"] / 1000, 2)
    if activities["total_duration"] >= 3600:
        activities["total_duration_hours"] = round(
            activities["total_duration"] / 3600, 2
        )

    # Add new request for previous year totals, only include totals
    prev_data = garth.connectapi(
        f"userstats-service/statistics/previousDays/{display_name}"
    )
    assert isinstance(prev_data, dict), f"Expected dict, got {type(prev_data)}"
    prev_metrics = prev_data["userMetrics"][0]
    last_12_months_totals = {
        "total_activities": prev_metrics["totalActivities"],
        "total_distance": prev_metrics["totalDistance"],
        "total_duration": prev_metrics["totalDuration"],
        "total_calories": prev_metrics["totalCalories"],
        "total_elevation_gain": prev_metrics["totalElevationGain"],
    }
    if last_12_months_totals["total_distance"] >= 1000:
        last_12_months_totals["total_distance_km"] = round(
            last_12_months_totals["total_distance"] / 1000, 2
        )
    if last_12_months_totals["total_duration"] >= 3600:
        last_12_months_totals["total_duration_hours"] = round(
            last_12_months_totals["total_duration"] / 3600, 2
        )

    # Get detailed lifetime totals and convert to snake_case
    try:
        lt = garth.connectapi(
            f"usersummary-service/stats/connectLifetimeTotals/{display_name}"
        )
    except Exception:
        # Investigate why for some users this endpoint raises 403 using the display_name
        lifetime_totals = {}
    else:
        assert isinstance(lt, dict), f"Expected dict, got {type(lt)}"
        lifetime_totals = {
            "total_distance": lt["totalDistance"],
            "total_distance_km": round(lt["totalDistance"] / 1000, 2),
            "total_steps": lt["totalSteps"],
            "total_calories": lt["totalCalories"],
            "total_goals_met_in_days": lt["totalGoalsMetInDays"],
            "total_active_days": lt["totalActiveDays"],
            "total_wellness_distance": lt["totalWellnessDistance"],
            "total_wellness_distance_km": round(lt["totalWellnessDistance"] / 1000, 2),
            "total_step_calories": lt["totalStepCalories"],
        }

    # Organize final stats dictionary as requested
    stats = {
        "lifetime_totals": {
            "activities": activities,
            "lifetime_totals": lifetime_totals,
        },
        "last_12_months": last_12_months_totals,
    }

    return stats


@server.tool()
@requires_garth_session
def weekly_intensity_minutes(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyIntensityMinutes]:
    """
    Weekly intensity minutes summary over a lookback window.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - weeks: Number of weeks to include ending at end_date. Default 1.

    Behavior
    - Returns a list of WeeklyIntensityMinutes objects (one per week) as JSON.
    - Fields typically include weeklyGoal, moderateValue, vigorousValue, calendarDate.
    """
    return garth.WeeklyIntensityMinutes.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_body_battery(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyBodyBatteryStress]:
    """
    Daily Body Battery and stress streams for a date range.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.

    Behavior
    - Returns JSON per day including arrays of timestamps and values for stress/bodyBattery.
    - Some samples may be MODELED/ADJUSTED; treat as estimates vs measured.
    """
    return garth.DailyBodyBatteryStress.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_hydration(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHydration]:
    """
    Daily hydration totals per day.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.

    Behavior
    - Returns a list of daily records or an empty list if no data in range.
    """
    return garth.DailyHydration.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_steps(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySteps]:
    """
    Daily step counts per day.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.
    """
    return garth.DailySteps.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_steps(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklySteps]:
    """
    Total step counts aggregated by week.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - weeks: Number of weeks to include ending at end_date. Default 1.
    """
    return garth.WeeklySteps.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_hrv(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyHRV]:
    """
    Daily HRV summaries including last-night averages and baseline windows.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.

    Behavior
    - Returns per-day summary objects (e.g., weeklyAvg, lastNightAvg, status, baseline thresholds).
    """
    return garth.DailyHRV.list(end_date, days)


@server.tool()
@requires_garth_session
def hrv_data(end_date: date | None = None, days: int = 1) -> str | list[garth.HRVData]:
    """
    Detailed HRV data for each day (more granular than daily_hrv).

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.
    """
    return garth.HRVData.list(end_date, days)


@server.tool()
@requires_garth_session
def daily_sleep(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailySleep]:
    """
    Daily sleep summaries per day (duration, efficiency, scores).

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.
    """
    return garth.DailySleep.list(end_date, days)


# Tools using direct API calls


@server.tool()
@requires_garth_session
def get_activities(start: int = 0, limit: int = 20) -> ConnectAPIResponse:
    """
    List recent activities from Garmin Connect.

    Parameters
    ----------
    start : int, optional
        The zero-based index in the activity list from which to start returning results (default: 0).
    limit : int, optional
        The maximum number of activities to retrieve starting from 'start' (default: 20).

    Returns
    -------
    activities : list
        List of activity records (JSON). For convenience, user role and profile image fields are removed.

    Notes
    -----
    Use 'start' and 'limit' to paginate results: (0,20), (20,20), etc.
    """
    params = {
        "start": start,
        "limit": limit,
    }
    endpoint = "activitylist-service/activities/search/activities"
    endpoint += "?" + urlencode(params)
    activities = garth.connectapi(endpoint)
    assert isinstance(activities, list)

    # remove user roles and profile image urls
    for activity in activities:
        activity.pop("userRoles")
        activity.pop("ownerDisplayName")
        activity.pop("ownerProfileImageUrlSmall")
        activity.pop("ownerProfileImageUrlMedium")
        activity.pop("ownerProfileImageUrlLarge")

    return activities


@server.tool()
@requires_garth_session
def get_activities_by_date(date: str) -> ConnectAPIResponse:
    """
    Daily activity summary for a specific date.

    Parameters
    - date: YYYY-MM-DD

    Behavior
    - Returns daily summary JSON that can include steps, calories, intensity minutes, and activity chart data.
    """
    return garth.connectapi(f"wellness-service/wellness/dailySummaryChart/?date={date}")


@server.tool()
@requires_garth_session
def get_activity_details(activity_id: str) -> ConnectAPIResponse:
    """
    Detailed information for a specific activity.

    Parameters
    - activity_id: Garmin Connect activity ID

    Behavior
    - Returns a JSON object with metadata (distance, duration, type, start time) and summary statistics.
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}")


@server.tool()
@requires_garth_session
def get_activity_splits(activity_id: str) -> ConnectAPIResponse:
    """
    Lap/split data for a specific activity.

    Parameters
    - activity_id: Garmin Connect activity ID

    Behavior
    - Returns lap-level metrics (e.g., per km/mi) and totals, as JSON list or object depending on activity.
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/splits")


@server.tool()
@requires_garth_session
def get_activity_weather(activity_id: str) -> ConnectAPIResponse:
    """
    Weather snapshot associated with an activity.

    Parameters
    - activity_id: Garmin Connect activity ID

    Behavior
    - Returns JSON including temperature, humidity, wind, and provider info when available.
    """
    return garth.connectapi(f"activity-service/activity/{activity_id}/weather")


@server.tool()
@requires_garth_session
def get_respiration_data(date: str) -> ConnectAPIResponse:
    """
    Respiration (breaths per minute) timeline for a day.

    Parameters
    - date: YYYY-MM-DD

    Behavior
    - Returns arrays of timestamp/value pairs and summary stats when available.
    """
    return garth.connectapi(f"wellness-service/wellness/daily/respiration/{date}")


@server.tool()
@requires_garth_session
def get_spo2_data(date: str) -> ConnectAPIResponse:
    """
    Pulse oximetry (SpO2) acclimation data for a day.

    Parameters
    - date: YYYY-MM-DD

    Behavior
    - Returns JSON with daily acclimation values and/or timeline data when recorded.
    """
    return garth.connectapi(f"wellness-service/wellness/daily/spo2acclimation/{date}")


@server.tool()
@requires_garth_session
def get_blood_pressure(date: str) -> ConnectAPIResponse:
    """
    Blood pressure readings for a given day.

    Parameters
    - date: YYYY-MM-DD

    Behavior
    - Returns JSON list of readings with timestamps and systolic/diastolic values when available.
    """
    return garth.connectapi(f"bloodpressure-service/bloodpressure/dayview/{date}")


@server.tool()
@requires_garth_session
def get_devices() -> ConnectAPIResponse:
    """
    List devices registered to the user's account.

    Behavior
    - Returns JSON array of devices (model, serial, firmware, capabilities) when available.
    """
    return garth.connectapi("device-service/deviceregistration/devices")


@server.tool()
@requires_garth_session
def get_device_settings(device_id: str) -> ConnectAPIResponse:
    """
    Settings for a specific registered device.

    Parameters
    - device_id: Device ID from Garmin Connect

    Behavior
    - Returns JSON with device info and per-feature settings where applicable.
    """
    return garth.connectapi(
        f"device-service/deviceservice/device-info/settings/{device_id}"
    )


@server.tool()
@requires_garth_session
def get_gear() -> ConnectAPIResponse:
    """
    List user gear (e.g., shoes, equipment) linked to the profile.

    Behavior
    - Requires user profile to derive profileId.
    - Returns JSON list of gear items and attributes when configured.
    """
    profile = garth.UserProfile.get()
    return garth.connectapi(
        f"gear-service/gear/filterGear?userProfilePk={profile.profile_id}"
    )


@server.tool()
@requires_garth_session
def nightly_sleep(
    end_date: date | None = None, nights: int = 1, sleep_movement: bool = False
) -> str | list[garth.SleepData]:
    """
    Nightly sleep stats and stages, optionally including movement data.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - nights: Number of nights to include ending at end_date. Default 1.
    - sleep_movement: Include detailed movement timeline. For multi-night ranges this can be large.
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
    Daily stress timeline and summary statistics per day.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.
    """
    return garth.DailyStress.list(end_date, days)


@server.tool()
@requires_garth_session
def weekly_stress(
    end_date: date | None = None, weeks: int = 1
) -> str | list[garth.WeeklyStress]:
    """
    Weekly stress aggregates over a lookback window.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - weeks: Number of weeks to include ending at end_date. Default 1.
    """
    return garth.WeeklyStress.list(end_date, weeks)


@server.tool()
@requires_garth_session
def daily_intensity_minutes(
    end_date: date | None = None, days: int = 1
) -> str | list[garth.DailyIntensityMinutes]:
    """
    Daily intensity minutes (moderate/vigorous) per day.

    Parameters
    - end_date: Optional end date (inclusive). Defaults to today if omitted.
    - days: Number of days to include ending at end_date. Default 1.
    """
    return garth.DailyIntensityMinutes.list(end_date, days)


@server.tool()
@requires_garth_session
def monthly_activity_summary(month: int, year: int) -> ConnectAPIResponse:
    """
    Monthly activity calendar summary for a given month and year.

    Parameters
    - month: 1-12
    - year: four-digit year

    Behavior
    - Returns JSON with daily entries and summary counts used by the calendar view.
    """
    return garth.connectapi(f"mobile-gateway/calendar/year/{year}/month/{month}")


@server.tool()
@requires_garth_session
def snapshot(from_date: date, to_date: date) -> ConnectAPIResponse:
    """
    Consolidated snapshot for a date range.

    Parameters
    - from_date: YYYY-MM-DD
    - to_date: YYYY-MM-DD

    Behavior
    - Returns a high-level JSON summary across multiple domains (steps, stress, sleep, etc.).
    - Useful as a starting point to decide which specialized tools to call next.
    """
    return garth.connectapi(f"mobile-gateway/snapshot/detail/v2/{from_date}/{to_date}")


def main():
    server.run()


if __name__ == "__main__":
    main()
