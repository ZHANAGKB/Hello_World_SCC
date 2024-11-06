#!/usr/bin/env python
# coding: utf-8

import os
import requests
import pandas as pd
from time import sleep


# Function to get user repositories
def get_user_repos(username, repo_type, headers):
    """
    获取用户的仓库信息（作为 Owner 或 Member）
    """
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100&type={repo_type}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"请求 {repo_type} 仓库失败，状态码: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        for repo in data:
            repos.append({
                "项目名称": repo.get("name"),
                "项目描述": repo.get("description"),
                "Star 数": repo.get("stargazers_count"),
                "Fork 数": repo.get("forks_count"),
                "仓库 URL": repo.get("html_url"),
                "仓库所有者": repo.get("owner", {}).get("login")  # 提取仓库拥有者
            })

        page += 1

    return repos


def get_user_contributed(username, headers):
    """
    获取用户的 PushEvent、PullRequestEvent 和 IssuesEvent 的总数，以及参与过的唯一仓库数量
    """
    total_count = {"PushEvent": 0, "PullRequestEvent": 0, "IssuesEvent": 0}
    unique_repos = set()  # 用于存储唯一的仓库名称
    page = 1

    while True:
        url = f"https://api.github.com/users/{username}/events?page={page}&per_page=100"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"请求用户活动失败，状态码: {response.status_code}")
            break

        events = response.json()
        if not events:
            break

        # 遍历用户的活动，统计每种事件类型的总数并记录唯一仓库
        for event in events:
            repo_name = event["repo"]["name"]  # 获取仓库名称
            unique_repos.add(repo_name)  # 添加到集合中，集合会自动去重

            if event["type"] == "PushEvent":
                total_count["PushEvent"] += 1
            elif event["type"] == "PullRequestEvent":
                total_count["PullRequestEvent"] += 1
            elif event["type"] == "IssuesEvent":
                total_count["IssuesEvent"] += 1

        page += 1

    # 计算唯一仓库的数量
    total_count["参与过的仓库数量"] = len(unique_repos)

    # 创建 DataFrame
    df_total_count = pd.DataFrame([total_count])
    return df_total_count


def get_user_profile(username, headers):
    """
    获取用户的个人资料信息
    """
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
    profile_df = pd.DataFrame([profile])
    return profile_df


def get_organization_repos(organization_name, headers):
    """
    获取组织的所有仓库信息
    """
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{organization_name}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"请求组织仓库失败，状态码: {response.status_code}")
            print("响应内容:", response.json())
            break

        data = response.json()
        if not data:
            # print("未找到仓库数据或已到达仓库列表末尾。")
            break

        for repo in data:
            repos.append({
                "组织名称": organization_name,
                "仓库名称": repo.get("name"),
                "仓库描述": repo.get("description"),
                "Star 数": repo.get("stargazers_count"),
                "Fork 数": repo.get("forks_count"),
                "仓库 URL": repo.get("html_url")
            })

        page += 1

    repos_df = pd.DataFrame(repos)
    return repos_df


def get_organization_profile(organization_name, headers):
    """
    获取组织的资料信息
    """
    url = f"https://api.github.com/orgs/{organization_name}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"请求组织资料失败，状态码: {response.status_code}")
        print("响应内容:", response.json())
        return None

    org_data = response.json()
    profile = {
        "组织名称": org_data.get("login"),
        "公司/组织全名": org_data.get("name"),
        "描述": org_data.get("description"),
        "博客": org_data.get("blog"),
        "位置": org_data.get("location"),
        "邮箱": org_data.get("email"),
        "公开仓库数": org_data.get("public_repos"),
        "粉丝数": org_data.get("followers"),
        "成员数": org_data.get("members_count"),
        "GitHub 主页": org_data.get("html_url")
    }
    profile_df = pd.DataFrame([profile])
    return profile_df


def get_github_users(since, per_page, headers):
    # 基础 URL
    base_url = "https://api.github.com"
    url = f"{base_url}/users?since={since}&per_page={per_page}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return []


def fetch_all_github_users(start_since, per_page, num_pages, headers):
    all_users = []
    since = start_since

    for _ in range(num_pages):
        users = get_github_users(since, per_page, headers)

        if not users:
            break  # 如果未返回用户，结束循环

        all_users.extend(users)  # 将用户添加到总用户列表

        # 更新 `since` 为最后一个用户的 ID，以便获取下一个批次
        since = users[-1]['id']

        # 延时以避免触发 API 的速率限制
        sleep(0.01)

    return all_users

def get_data_collection(username, headers):
    # 获取用户作为 Owner 的仓库
    owner_repos = get_user_repos(username, "owner", headers)
    # 获取用户作为 Member 的仓库
    member_repos = get_user_repos(username, "member", headers)
    all_repos = owner_repos + member_repos
    # 合并两个列表
    df_user_repos = pd.DataFrame(all_repos)

    if df_user_repos.empty:
        # 如果为空，则跳过这次循环
        return None

    # 计算总和
    total_stars = df_user_repos["Star 数"].sum()
    total_forks = df_user_repos["Fork 数"].sum()
    # 创建一个新的 DataFrame 仅显示总数
    df_project_impact = pd.DataFrame({
        "Star 数": [total_stars],
        "Fork 数": [total_forks]
    })

    df_contributed_activity = get_user_contributed(username, headers)

    user_profile = get_user_profile(username, headers)

    df_user_social_network_impact = pd.DataFrame({
        "用户名": user_profile["用户名"],
        "国家": user_profile["国家"],
        "关注者数": user_profile["关注者数"],
        "关注中": user_profile["关注中"],
        "所属组织数量": user_profile["所属组织数量"]
    })
    user_result = pd.concat([df_user_social_network_impact, df_project_impact, df_contributed_activity], axis=1)

    # file_path = f"../doc/Data Source/{username}/userProfile.csv"
    # path = f"../doc/Data Source/{username}"
    # if not os.path.exists(path):
    #     os.mkdir(path)
    #     print(f"Directory '{path}' created successfully.")
    # else:
    #     print(f"Directory '{path}' already exists.")

    # user_result.to_csv(file_path, index=False, encoding='utf-8')

    return user_result

    # organizations = user_profile.at[0, "所属组织"]
    #
    # all_organization_repos = pd.DataFrame()
    #
    # for organization_name in organizations:
    #     # 获取每个组织的仓库信息
    #     organization_repos = get_organization_repos(organization_name, headers)
    #     # 合并到一个 DataFrame
    #     all_organization_repos = pd.concat([all_organization_repos, organization_repos], ignore_index=True)
    #
    # if all_organization_repos.empty:
    #     # 如果为空，则跳过这次循环
    #     return
    #
    # aggregated_repos = all_organization_repos.groupby("组织名称")[["Star 数", "Fork 数"]].sum().reset_index()
    #
    # # 正确的方法是使用一个循环来获取每个组织的信息
    # all_organization_profile = pd.DataFrame()
    #
    # for organization_name in organizations:
    #     # 获取每个组织的仓库信息
    #     organization_profile = get_organization_profile(organization_name, headers)
    #     # 合并到一个 DataFrame
    #     all_organization_profile = pd.concat([all_organization_profile, organization_profile], ignore_index=True)
    #
    # if all_organization_profile.empty:
    #     # 如果为空，则跳过这次循环
    #     return
    #
    # merged_df = pd.merge(
    #     all_organization_profile,
    #     aggregated_repos,
    #     on="组织名称",
    #     how="inner"
    # )
    # # 只保留指定的列
    # result_df = merged_df[[
    #     "组织名称",
    #     "公司/组织全名",
    #     "位置",
    #     "Star 数",
    #     "Fork 数",
    #     "公开仓库数",
    #     "粉丝数",
    #     "成员数"
    # ]]
    #
    # file_path = f"../doc/Data Source/{username}/companyProfile.csv"
    # result_df.to_csv(file_path, index=False, encoding='utf-8')


# def main():
#     # 主程序逻辑
#     GITHUB_TOKEN = "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"
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#     file_path = f"../doc/Data Source/all_user_profile.csv"
#     users = fetch_all_github_users(start_since=0, per_page=100, num_pages=10, headers=headers)
#
#     all_user_profile = pd.DataFrame()
#     for user in users:
#         print(user['login'])
#         username = user['login']
#         user_profile = get_data_collection(username, headers)
#         if user_profile is not None:
#             all_user_profile = pd.concat([all_user_profile, user_profile], ignore_index=True)
#             all_user_profile.to_csv(file_path, index=False, encoding='utf-8')
#         sleep(0.01)
#
#
# if __name__ == "__main__":
#     main()
