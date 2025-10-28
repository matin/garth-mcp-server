import json
from fastmcp.client import Client
from garth.users.profile import UserProfile

async def test_list_tools(mcp_client: Client):
    list_tools = await mcp_client.list_tools()

    assert len(list_tools) > 0



async def test_get_profile(mcp_client: Client):
    response = await mcp_client.call_tool("user_profile")
    #breakpoint()
    profile_data = json.loads(response.content[0].text)

    assert response.is_error is False
    assert response.content[0].type == "text"
    assert UserProfile(**profile_data)
