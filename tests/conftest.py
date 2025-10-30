import os
import pytest
import vcr
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from garth_mcp_server import server


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


def sanitize_cookie(cookie_value) -> str:
    """Sanitize cookie values."""
    import re
    return re.sub(r"=[^;]*", "=SANITIZED", cookie_value)


def sanitize_request(request):
    """Sanitize sensitive data from requests."""
    import re

    if request.body:
        try:
            body = request.body.decode("utf8")
        except UnicodeDecodeError:
            pass
        else:
            for key in ["username", "password", "refresh_token", "mfa_token", "access_token"]:
                body = re.sub(key + r"=[^&]*", f"{key}=SANITIZED", body)
            request.body = body.encode("utf8")

    if "Cookie" in request.headers:
        cookies = request.headers["Cookie"].split("; ")
        sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
        request.headers["Cookie"] = "; ".join(sanitized_cookies)
    return request


def sanitize_response(response):
    """Sanitize sensitive data from responses."""
    import re
    import json
    import gzip
    import io

    try:
        encoding = response["headers"].pop("Content-Encoding")
    except KeyError:
        pass
    else:
        if encoding[0] == "gzip":
            body = response["body"]["string"]
            buffer = io.BytesIO(body)
            try:
                body = gzip.GzipFile(fileobj=buffer).read()
            except gzip.BadGzipFile:
                pass
            else:
                response["body"]["string"] = body

    for key in ["set-cookie", "Set-Cookie"]:
        if key in response["headers"]:
            cookies = response["headers"][key]
            sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
            response["headers"][key] = sanitized_cookies

    try:
        body = response["body"]["string"].decode("utf8")
    except UnicodeDecodeError:
        pass
    else:
        patterns = [
            "oauth_token=[^&]*",
            "oauth_token_secret=[^&]*",
            "mfa_token=[^&]*",
        ]
        for pattern in patterns:
            body = re.sub(pattern, pattern.split("=")[0] + "=SANITIZED", body)
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            pass
        else:
            if body_json and isinstance(body_json, dict):
                for field in [
                    "access_token",
                    "refresh_token",
                    "jti",
                    "consumer_key",
                    "consumer_secret",
                ]:
                    if field in body_json:
                        body_json[field] = "SANITIZED"

                # Sanitize personal information with fake values
                if "displayName" in body_json:
                    body_json["displayName"] = "testuser"
                if "fullName" in body_json:
                    body_json["fullName"] = "Test User"
                # if "userName" in body_json:
                #     body_json["userName"] = "testuser"
                if "location" in body_json:
                    body_json["location"] = "Test City, Test Country"
                if "garminGUID" in body_json:
                    body_json["garminGUID"] = "00000000-0000-0000-0000-000000000000"

            body = json.dumps(body_json)
        response["body"]["string"] = body.encode("utf8")

    return response


@pytest.fixture(scope="session")
def vcr_config():
    """VCRpy configuration for recording HTTP interactions."""
    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "once",  # Record once, then replay
        "filter_headers": [("Authorization", "Bearer SANITIZED")],
        "before_record_request": sanitize_request,
        "before_record_response": sanitize_response,
    }


@pytest.fixture
async def mcp_client():
    """MCP client fixture for testing."""
    async with Client[FastMCPTransport](transport=server) as client:
        yield client


@pytest.fixture
def mock_garmin_token():
    """Mock Garmin token for testing."""
    return os.getenv("GARTH_TOKEN", "mock_token_for_testing")


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "activityId": 20765926243,
        "activityName": "Yoga",
        "activityType": {"typeId": 52, "typeKey": "yoga", "parentTypeId": 17},
        "startTimeLocal": "2025-10-27T12:00:00",
        "startTimeGMT": "2025-10-27T16:00:00",
        "duration": 1800,  # 30 minutes
        "distance": 0.0,
        "calories": 150,
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile data for testing."""
    return {
        "displayName": "Test User",
        "fullName": "Test User",
        "email": "test@example.com",
        "username": "testuser",
        "memberSince": "2020-01-01T00:00:00.000Z",
        "location": "Test City, Test Country",
        "dateOfBirth": "1990-01-01",
        "height": 175.0,
        "weight": 70.0,
        "gender": "MALE",
    }


@pytest.fixture
def sample_daily_steps():
    """Sample daily steps data for testing."""
    return {
        "calendar_date": "2025-10-27",
        "step_goal": 10000,
        "total_distance": 5000,
        "total_steps": 8500,
    }
