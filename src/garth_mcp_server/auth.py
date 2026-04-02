"""CLI tool for authenticating with Garmin Connect (MFA supported).

Uses a manual SSO flow with delays between requests to avoid Garmin's
aggressive rate limiting on the /sso/signin endpoint.
"""

import getpass
import re
import sys
import time

import garth
import garth.sso as sso


def main():
    client = garth.client

    SSO = f"https://sso.{client.domain}/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = dict(id="gauth-widget", embedWidget="true", gauthHost=SSO)
    SIGNIN_PARAMS = {
        **SSO_EMBED_PARAMS,
        "gauthHost": SSO_EMBED,
        "service": SSO_EMBED,
        "source": SSO_EMBED,
        "redirectAfterAccountLoginUrl": SSO_EMBED,
        "redirectAfterAccountCreationUrl": SSO_EMBED,
    }

    email = input("Garmin email: ")
    password = getpass.getpass("Garmin password: ")

    try:
        # Step 1: Set cookies
        resp1 = client.sess.get(f"{SSO}/embed", params=SSO_EMBED_PARAMS, timeout=15)
        resp1.raise_for_status()

        # Step 2: Get CSRF token
        time.sleep(1)
        resp2 = client.sess.get(
            f"{SSO}/signin",
            params=SIGNIN_PARAMS,
            headers={"referer": resp1.url},
            timeout=15,
        )
        resp2.raise_for_status()
        csrf = sso.get_csrf_token(resp2.text)

        # Step 3: Submit credentials
        time.sleep(2)
        resp3 = client.sess.post(
            f"{SSO}/signin",
            params=SIGNIN_PARAMS,
            headers={"referer": resp2.url},
            data={
                "username": email,
                "password": password,
                "embed": "true",
                "_csrf": csrf,
            },
            timeout=15,
        )
        resp3.raise_for_status()
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)

    title = re.search(r"<title>(.*?)</title>", resp3.text)
    title_text = title.group(1) if title else ""

    # Step 4: Handle MFA if needed
    if "MFA" in title_text:
        mfa_code = input("MFA code: ")
        csrf2 = sso.get_csrf_token(resp3.text)
        time.sleep(1)
        try:
            resp4 = client.sess.post(
                f"{SSO}/verifyMFA/loginEnterMfaCode",
                params=SIGNIN_PARAMS,
                headers={"referer": resp3.url},
                data={
                    "embed": "true",
                    "_csrf": csrf2,
                    "fromPage": "setupEnterMfaCode",
                    "mfa-code": mfa_code,
                },
                timeout=15,
            )
            resp4.raise_for_status()
        except Exception as e:
            print(f"MFA verification failed: {e}", file=sys.stderr)
            sys.exit(1)
        client.last_resp = resp4
    else:
        client.last_resp = resp3

    # Step 5: Exchange ticket for OAuth tokens
    title = re.search(r"<title>(.*?)</title>", client.last_resp.text)
    title_text = title.group(1) if title else ""

    if title_text != "Success" and not re.search(
        r'ticket=([^"]+)"', client.last_resp.text
    ):
        print(f"Login failed. Page title: {title_text}", file=sys.stderr)
        sys.exit(1)

    try:
        oauth1, oauth2 = sso._complete_login(client)
        client.oauth1_token = oauth1
        client.oauth2_token = oauth2
    except Exception as e:
        print(f"Token exchange failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(client.dumps())
