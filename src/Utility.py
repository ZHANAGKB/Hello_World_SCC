
import requests
import pandas as pd
from collections import Counter


def get_user_profile_nation_detect(username):
    """
    获取用户的个人资料信息，并分别获取关注者和关注中的人的国家信息，更新用户国家信息
    """
    GITHUB_TOKEN = "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"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 获取用户的个人资料
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"请求用户资料失败，状态码: {response.status_code}")
        return None

    profile_data = response.json()
    location = profile_data.get("location")

    # 清洗用户的国家信息
    if not location or any(char in location for char in ['#', '%', '&', '*', '乱码']):
        location = "Unknown"

    profile = {
        "用户名": profile_data.get("login"),
        "全名": profile_data.get("name"),
        "公司": profile_data.get("company"),
        "博客": profile_data.get("blog"),
        "国家": location,  # 使用清洗后的国家信息
        "邮箱": profile_data.get("email"),
        "简介": profile_data.get("bio"),
        "公开仓库数": profile_data.get("public_repos"),
        "关注者数": profile_data.get("followers"),
        "关注中": profile_data.get("following"),
        "GitHub 个人主页": profile_data.get("html_url")
    }

    # 获取关注者的国家信息
    follower_nations = []
    followers_url = f"https://api.github.com/users/{username}/followers"
    followers_response = requests.get(followers_url, headers=headers)
    if followers_response.status_code == 200:
        followers = followers_response.json()
        for user in followers:
            user_url = user.get("url")  # 获取每个用户的详细资料 URL
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_location = user_data.get("location")
                # 仅在 user_location 有效时添加
                if user_location and not any(char in user_location for char in ['#', '%', '&', '*', '乱码']):
                    follower_nations.append(user_location)

    # 获取“关注中”用户的国家信息
    following_nations = []
    following_url = f"https://api.github.com/users/{username}/following"
    following_response = requests.get(following_url, headers=headers)
    if following_response.status_code == 200:
        following = following_response.json()
        for user in following:
            user_url = user.get("url")  # 获取每个用户的详细资料 URL
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_location = user_data.get("location")
                # 仅在 user_location 有效时添加
                if user_location and not any(char in user_location for char in ['#', '%', '&', '*', '乱码']):
                    following_nations.append(user_location)

    # 统计出现最多的国家
    most_common_follower_nation = Counter(follower_nations).most_common(1)[0][0] if follower_nations else None
    most_common_following_nation = Counter(following_nations).most_common(1)[0][0] if following_nations else None

    # 更新用户国家信息
    if location == "Unknown":
        if most_common_follower_nation and most_common_following_nation:
            if most_common_follower_nation == most_common_following_nation:
                location = most_common_follower_nation  # 两个国家相同，直接使用
            else:
                location = most_common_following_nation  # 不同则使用 "following" 出现最多的国家
        elif most_common_following_nation:
            location = most_common_following_nation
        elif most_common_follower_nation:
            location = most_common_follower_nation

    profile["国家"] = location
    profile["关注者出现最多的国家"] = most_common_follower_nation
    profile["关注中出现最多的国家"] = most_common_following_nation

    # profile_df = pd.DataFrame([profile])
    return profile


def search_repositories_by_language_and_topic(language, topic, headers):
    """
    使用 GitHub 搜索 API 组合搜索项目，按编程语言和主题标签筛选
    """
    # 构建搜索查询
    query = f"language:{language}+topic:{topic}"
    url = f"https://api.github.com/search/repositories?q={query}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repositories = response.json().get('items', [])
        for repo in repositories:
            print(f"项目名: {repo['name']}, 拥有者: {repo['owner']['login']}, 项目主页: {repo['html_url']}")
    else:
        print(f"请求失败，状态码: {response.status_code}")

    return