"""
Utility functions for the Garth MCP Server.
"""


def remove_keys_if_exists(
    data: dict | list[dict], keys_to_remove: list[str]
) -> dict | list[dict]:
    """
    Remove specified keys from a dictionary or list of dictionaries if they exist.

    Parameters
    ----------
    data : dict | list[dict]
        The dictionary or list of dictionaries to remove keys from
    keys_to_remove : list[str]
        List of keys to remove

    Returns
    -------
    dict | list[dict]
        The dictionary or list of dictionaries with specified keys removed
    """
    if isinstance(data, dict):
        for key in keys_to_remove:
            data.pop(key, None)
        return data
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for key in keys_to_remove:
                    item.pop(key, None)
        return data
    else:
        return data
