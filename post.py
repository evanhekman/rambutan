import os
import sys
import time
import dotenv
import requests
import google.generativeai as genai
from requests_oauthlib import OAuth1


dotenv.load_dotenv(override=True)


def generate_post(agent_name):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt_path = os.path.join(agent_name, "prompt.txt")
    with open(prompt_path, "r") as f:
        prompt = f.read()

    response = model.generate_content(prompt).text
    response = response.replace("\n", " ")
    response = response.replace("\r", " ")
    response = response.replace("\t", " ")
    response = response.replace("  ", " ")

    output_path = os.path.join(agent_name, "output.txt")
    with open(output_path, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"\n\n{timestamp}\n")
        f.write(response)

    return response


def validate_post(post):
    if len(post) > 280:
        print(f"Post is too long: {len(post)} chars.")
        return False
    if len(post) < 8:
        print(f"Post is too short: {len(post)} chars.")
        return False
    print("generated post:\n", post)
    yesno = input("type 'post' to post to x: ")
    return yesno == "post"


def ship_post(post):
    url = "https://api.twitter.com/2/tweets"
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_KEY_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    print("api_key:", api_key)
    print("api_secret:", api_secret)
    print("access_token:", access_token)
    print("access_token_secret:", access_token_secret)

    response = requests.post(
        url,
        auth=OAuth1(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        ),
        json={"text": post},
    )

    if response.status_code == 201:
        print("Tweet posted successfully!")
        return response.json()
    else:
        print(f"Failed to post tweet. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <agent_name>")
        sys.exit(1)

    agent_name = sys.argv[1]
    post = generate_post(agent_name)
    if validate_post(post):
        print("validated post")
        ship_post(post)
        exit(0)
    else:
        print("failed to validate post, not posting")
        exit(0)


if __name__ == "__main__":
    main()
