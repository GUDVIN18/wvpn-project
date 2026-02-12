import requests
from datetime import datetime, timezone

BASE_URL = "https://wvpn.fr2.xraygopaydonat1.ru:9081"

# resp = requests.post(
#     f"{BASE_URL}/api/admin/token",
#     data={
#         "username": "user",
#         "password": "super_password"
#     }
# )
# access_token = resp.json()["access_token"]
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiYWNjZXNzIjoic3VkbyIsImlhdCI6MTc3MDgyMjc3MCwiZXhwIjo0OTI0NDIyNzcwfQ.2maNcd0nB1XG6vikG3d4WULPTTmDjmTvd7xZRv9dgKw"
# print(f"Access token: {access_token}")

HEADERS = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def get_vless_inbounds() -> list[str]:
    """Получить все VLESS inbound-теги из панели"""
    resp = requests.get(f"{BASE_URL}/api/inbounds", headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    if "vless" not in data:
        raise RuntimeError("No vless inbounds returned by API")

    return [item["tag"] for item in data["vless"]]


def create_user_api(
        username: str,
        expire: int
):
    try:
        vless_inbounds = get_vless_inbounds()

        payload = {
            "username": username,
            "status": "active",
            "expire": expire,
            "data_limit": 0,
            "data_limit_reset_strategy": "no_reset",

            "inbounds": {
                "vless": vless_inbounds
            },

            "proxies": {
                "vless": {
                    "flow": "xtls-rprx-vision"
                }
            },

            "note": "",
        }

        resp = requests.post(
            f"{BASE_URL}/api/user",
            headers=HEADERS,
            json=payload,
            timeout=15,
        )

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"{resp.status_code} {resp.text}")
        print("User created successfully")
        return f'{BASE_URL}{resp.json().get("subscription_url")}'
    except Exception as e:
        print(f"Error creating user: {e}")
        raise

def update_user_api(
        username: str,
        status: str,
        expire: int,
):
    vless_inbounds = get_vless_inbounds()

    payload = {
        "username": username,
        "status": status,
        "expire": expire,  # 11 Feb 2026 UTC
        # "data_limit": 0,
        # "data_limit_reset_strategy": "no_reset",

        "inbounds": {
            "vless": vless_inbounds
        },

        "proxies": {
            "vless": {
                "flow": "xtls-rprx-vision"
            }
        },

        "note": "",
    }

    resp = requests.put(
        f"{BASE_URL}/api/user/{username}",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )

    if resp.status_code not in (200, 201):
        raise RuntimeError(f"{resp.status_code} {resp.text}")
    print("User update successfully")
    return f'{BASE_URL}{resp.json().get("subscription_url")}'



if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_builder.settings')
    django.setup()

    from apps.bot.models import BotUser

    # users = BotUser.objects.filter(tg_id__in=[6424595615])
    users = BotUser.objects.all()

    for user in users:
        try:
            if not user.subscription:
                print(f"No subscription date for {user.tg_id}")
                continue

            subscription_url = create_user_api(
                username=str(user.tg_id),
                expire=int(user.subscription_date_end.timestamp())
            )

            print(f"Created for {user.tg_id}: {subscription_url}")
            user.vpn_key = subscription_url
            user.save()

        except Exception as e:
            print(f"Error creating user {user.tg_id}: {e}")