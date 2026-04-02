"""CLI tool for authenticating with Garmin Connect (MFA supported)."""

import getpass
import sys

import garth


def main():
    email = input("Garmin email: ")
    password = getpass.getpass("Garmin password: ")
    try:
        garth.login(email, password)
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(garth.client.dumps())
