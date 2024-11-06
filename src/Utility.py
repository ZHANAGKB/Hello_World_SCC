
import requests
import pandas as pd


def get_user_profile(username):
    """
    获取用户的个人资料信息
    """
    GITHUB_TOKEN = "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"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"请求用户资料失败，状态码: {response.status_code}")
        print("响应内容:", response.json())
        return None

    profile_data = response.json()
    profile = {
        "用户名": profile_data.get("login"),
        "全名": profile_data.get("name"),
        "公司": profile_data.get("company"),
        "博客": profile_data.get("blog"),
        "国家": profile_data.get("location"),
        "邮箱": profile_data.get("email"),
        "简介": profile_data.get("bio"),
        "公开仓库数": profile_data.get("public_repos"),
        "关注者数": profile_data.get("followers"),
        "关注中": profile_data.get("following"),
        "GitHub 个人主页": profile_data.get("html_url")
    }
    # 获取用户所属组织信息
    orgs_url = f"https://api.github.com/users/{username}/orgs"
    orgs_response = requests.get(orgs_url, headers=headers)

    if orgs_response.status_code == 200:
        organizations = [org.get("login") for org in orgs_response.json()]
        profile["所属组织"] = organizations
        profile["所属组织数量"] = len(organizations)  # 添加所属组织数量
    else:
        print(f"请求用户组织信息失败，状态码: {orgs_response.status_code}")
        profile["所属组织"] = []
        profile["所属组织数量"] = 0  # 如果请求失败，组织数量为 0
    # profile_df = pd.DataFrame([profile])
    return profile
