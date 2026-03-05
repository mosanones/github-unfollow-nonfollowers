#!/usr/bin/env python3
"""
GitHub Unfollow Non-Followers
A script to unfollow GitHub users who don't follow you back.
"""

import argparse
import sys
import time
from typing import List, Dict, Optional
import requests
from config import GITHUB_TOKEN, GITHUB_USERNAME, API_BASE_URL, REQUEST_TIMEOUT


class GitHubUnfollower:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = API_BASE_URL
        
    def make_request(self, url: str, method: str = 'GET', params: Optional[Dict] = None) -> List:
        """Make a paginated request to GitHub API."""
        results = []
        page = 1
        
        while True:
            if params:
                params['page'] = page
                params['per_page'] = 100
            else:
                params = {'page': page, 'per_page': 100}
                
            try:
                if method == 'GET':
                    response = requests.get(
                        url, 
                        headers=self.headers, 
                        params=params,
                        timeout=REQUEST_TIMEOUT
                    )
                elif method == 'DELETE':
                    response = requests.delete(
                        url,
                        headers=self.headers,
                        timeout=REQUEST_TIMEOUT
                    )
                    if response.status_code == 204:
                        return [{'success': True}]
                    return []
                
                response.raise_for_status()
                
                # Check rate limit
                remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
                if remaining < 10:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    sleep_time = max(reset_time - time.time(), 0) + 1
                    print(f"\n⚠️  Rate limit low. Sleeping for {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time)
                
                page_results = response.json()
                if not page_results:
                    break
                    
                if isinstance(page_results, list):
                    results.extend(page_results)
                else:
                    return [page_results]
                
                if len(page_results) < 100:
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error making request: {e}")
                break
                
        return results
    
    def get_followers(self) -> List[str]:
        """Get list of followers."""
        print("📥 Fetching followers...")
        url = f"{self.base_url}/users/{self.username}/followers"
        followers = self.make_request(url)
        followers_list = [follower['login'] for follower in followers]
        print(f"✓ Found {len(followers_list)} followers")
        return followers_list
    
    def get_following(self) -> List[str]:
        """Get list of users being followed."""
        print("📥 Fetching following...")
        url = f"{self.base_url}/users/{self.username}/following"
        following = self.make_request(url)
        following_list = [user['login'] for user in following]
        print(f"✓ Following {len(following_list)} users")
        return following_list
    
    def find_non_followers(self, followers: List[str], following: List[str]) -> List[str]:
        """Find users you follow who don't follow you back."""
        followers_set = set(followers)
        return [user for user in following if user not in followers_set]
    
    def unfollow_user(self, username: str) -> bool:
        """Unfollow a specific user."""
        url = f"{self.base_url}/user/following/{username}"
        result = self.make_request(url, method='DELETE')
        return bool(result)
    
    def run(self, perform_unfollow: bool = False):
        """Main execution function."""
        print(f"\n🔍 Analyzing GitHub follow relationships for @{self.username}")
        print("=" * 50)
        
        # Get followers and following
        followers = self.get_followers()
        following = self.get_following()
        
        # Find non-followers
        non_followers = self.find_non_followers(followers, following)
        
        if not non_followers:
            print("\n✅ Great! Everyone you follow follows you back!")
            return
        
        print(f"\n📊 Analysis complete!")
        print(f"You are following {len(non_followers)} users who don't follow you back:")
        print("-" * 40)
        
        for i, user in enumerate(non_followers, 1):
            print(f"{i:3}. {user} (https://github.com/{user})")
        
        if perform_unfollow:
            print(f"\n🔄 Starting to unfollow {len(non_followers)} users...")
            success_count = 0
            
            for i, user in enumerate(non_followers, 1):
                print(f"  {i}/{len(non_followers)} Unfollowing @{user}... ", end='')
                
                if self.unfollow_user(user):
                    print("✓")
                    success_count += 1
                else:
                    print("❌")
                
                # Small delay to avoid hitting rate limits
                time.sleep(0.5)
            
            print(f"\n✅ Successfully unfollowed {success_count} users!")
            if success_count < len(non_followers):
                print(f"❌ Failed to unfollow {len(non_followers) - success_count} users")
        else:
            print(f"\n💡 Preview mode - No users were unfollowed.")
            print(f"   Run with --unfollow to actually unfollow these {len(non_followers)} users.")


def main():
    parser = argparse.ArgumentParser(
        description='Unfollow GitHub users who do not follow you back'
    )
    parser.add_argument(
        '--unfollow',
        action='store_true',
        help='Actually perform the unfollow actions (default is preview only)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview who would be unfollowed (default behavior)'
    )
    
    args = parser.parse_args()
    
    # Check credentials
    if GITHUB_TOKEN == 'your_token_here' or GITHUB_USERNAME == 'your_username_here':
        print("❌ Error: Please configure your GitHub token and username in config.py")
        print("   or set GITHUB_TOKEN and GITHUB_USERNAME environment variables")
        sys.exit(1)
    
    # Create unfollower instance
    unfollower = GitHubUnfollower(GITHUB_TOKEN, GITHUB_USERNAME)
    
    try:
        # Run the unfollow process
        unfollower.run(perform_unfollow=args.unfollow)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
