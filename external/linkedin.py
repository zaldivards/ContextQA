import requests

URL = (
    "https://gist.githubusercontent.com/emarco177/0d6a3f93dd06634d95e46a2782ed7490/raw/fad4d7a8"
    "7e3e934ad52ba2a968bad9eb45128665/eden-marco.json"
)


def get_linkedin_profile(url: str = URL):
    response = requests.get(url, timeout=20)

    data = {
        key: value
        for key, value in response.json().items()
        if value and key not in ("people_also_viewed", "certifications")
    }
    for group in data.get("groups", []):
        group.pop("profile_pic_url")

    return data
