import requests
from datetime import datetime, timezone

BASE_URL = "https://wvpn.fr2.xraygopaydonat1.ru:9081"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiYWNjZXNzIjoic3VkbyIsImlhdCI6MTc3MDcxOTMwMCwiZXhwIjoxNzcwODA1NzAwfQ.bcYkHf8tAV_lc0pvWh0Zxht_88Lr91oSsgyFvIVrKng"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
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
    result = create_user_api("456565666", int(datetime(2026, 2, 15, tzinfo=timezone.utc).timestamp()))
    print(result)