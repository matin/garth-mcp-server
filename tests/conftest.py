import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from garth_mcp_server import server


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def mcp_client():
    async with Client[FastMCPTransport](transport=server) as client:
        yield client
