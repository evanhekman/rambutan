import requests
from requests_oauthlib import OAuth1
import os


def post_to_x(post):
    # API endpoint for posting tweets
    url = "https://api.twitter.com/2/tweets"

    # Get credentials from environment variables
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_KEY_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    # Create OAuth1 authentication object
    auth = OAuth1(api_key, api_secret, access_token, access_token_secret)

    # Set up the payload
    payload = {"text": post}

    # Make the POST request with OAuth1
    response = requests.post(url, auth=auth, json=payload)

    # Check if the request was successful
    if response.status_code == 201:
        print("Tweet posted successfully!")
        return response.json()
    else:
        print(f"Failed to post tweet. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
