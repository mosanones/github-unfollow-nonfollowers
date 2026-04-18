"""GitHub API client for managing followers and following."""

import time
import requests
from config import GITHUB_TOKEN, GITHUB_USERNAME, API_BASE_URL, REQUEST_DELAY


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        self.username = GITHUB_USERNAME
        self.base_url = API_BASE_URL

    def _get_paginated(self, url: str) -> list:
        """Fetch all pages of a paginated GitHub API endpoint."""
        results = []
        page = 1
        while True:
            response = self.session.get(url, params={"per_page": 100, "page": page})
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            results.extend(data)
            page += 1
            time.sleep(REQUEST_DELAY)
        return results

    def get_followers(self) -> set:
        """Return a set of usernames who follow the authenticated user."""
        url = f"{self.base_url}/users/{self.username}/followers"
        followers = self._get_paginated(url)
        return {user["login"] for user in followers}

    def get_following(self) -> set:
        """Return a set of usernames the authenticated user is following."""
        url = f"{self.base_url}/users/{self.username}/following"
        following = self._get_paginated(url)
        return {user["login"] for user in following}

    def unfollow_user(self, username: str) -> bool:
        """Unfollow a GitHub user. Returns True on success, False otherwise."""
        url = f"{self.base_url}/user/following/{username}"
        response = self.session.delete(url)
        time.sleep(REQUEST_DELAY)
        if response.status_code == 204:
            return True
        # 404 means we weren't following them anyway, treat as success
        if response.status_code == 404:
            return True
        print(f"  [!] Failed to unfollow {username}: HTTP {response.status_code}")
        return False

    def get_non_followers(self) -> set:
        """Return users the authenticated user follows who don't follow back."""
        followers = self.get_followers()
        following = self.get_following()
        non_followers = following - followers
        # Print a quick summary so I can see the numbers at a glance
        print(f"  [i] Following: {len(following)}, Followers: {len(followers)}, Not following back: {len(non_followers)}")
        return non_followers
