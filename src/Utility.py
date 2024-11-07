from collections import Counter
import requests
import os

# 将 GitHub Token 从硬编码改为环境变量的读取方式
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_user_profile(username):
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
    # orgs_url = f"https://api.github.com/users/{username}/orgs"
    # orgs_response = requests.get(orgs_url, headers=headers)
    #
    # if orgs_response.status_code == 200:
    #     organizations = [org.get("login") for org in orgs_response.json()]
    #     profile["所属组织"] = organizations
    #     profile["所属组织数量"] = len(organizations)  # 添加所属组织数量
    # else:
    #     print(f"请求用户组织信息失败，状态码: {orgs_response.status_code}")
    #     profile["所属组织"] = []
    #     profile["所属组织数量"] = 0  # 如果请求失败，组织数量为 0
    # profile_df = pd.DataFrame([profile])
    return profile


def get_user_profile_nation_detect(username):
    """
    获取用户的个人资料信息，并分别获取关注者和关注中的人的国家信息，更新用户国家信息
    """


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

    if location == "Unknown":
        # 获取互相关注用户的国家信息
        mutual_follow_nations = []

        # 获取关注者列表
        followers_url = f"https://api.github.com/users/{username}/followers"
        followers_response = requests.get(followers_url, headers=headers)
        if followers_response.status_code == 200:
            followers = followers_response.json()

            for follower in followers:
                follower_name = follower['login']
                # 检查互相关注
                following_url = f"https://api.github.com/users/{follower_name}/following/{username}"
                following_response = requests.get(following_url, headers=headers)

                if following_response.status_code == 204:  # 如果互相关注
                    # 获取该互相关注者的位置信息
                    follower_profile_url = f"https://api.github.com/users/{follower_name}"
                    follower_profile_response = requests.get(follower_profile_url, headers=headers)
                    if follower_profile_response.status_code == 200:
                        follower_data = follower_profile_response.json()
                        follower_location = follower_data.get("location")
                        # 清洗并记录互相关注者的有效国家信息
                        if follower_location and not any(
                                char in follower_location for char in ['#', '%', '&', '*', '乱码']):
                            mutual_follow_nations.append(follower_location)

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
        most_common_follower_nation = Counter(mutual_follow_nations).most_common(1)[0][
            0] if mutual_follow_nations else None
        most_common_following_nation = Counter(following_nations).most_common(1)[0][0] if following_nations else None

        # 更新用户国家信息
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
        # print(mutual_follow_nations)

    # profile_df = pd.DataFrame([profile])
    return profile


def get_user_total_stars(username):
    """
    获取用户的所有仓库的总 Star 数（包括用户作为 Owner 和 Member 的仓库）。
    """

    total_stars = 0

    # 遍历仓库类型（Owner 和 Member）
    for repo_type in ["owner", "member"]:
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

            # 累加每个仓库的 star 数
            for repo in data:
                total_stars += repo.get("stargazers_count", 0)

            page += 1

    return total_stars


def calculate_contribution_score(events):
    """
    根据用户的活动事件计算贡献分数，返回每个仓库的贡献分数和贡献评价。
    """
    weights = {
        "PushEvent": 0.4,
        "PullRequestEvent": 0.3,
        "IssuesEvent": 0.2,
        "ForkEvent": 0.05,
        "WatchEvent": 0.05
    }
    contribution_score = {}

    for event in events:
        repo_name = event["repo"]["name"]
        event_type = event["type"]

        # 初始化项目的贡献分数
        if repo_name not in contribution_score:
            contribution_score[repo_name] = 0

        # 更新贡献分数
        if event_type in weights:
            # 如果是 PullRequestEvent 并且未合并，权重减半
            if event_type == "PullRequestEvent" and not event.get("payload", {}).get("pull_request", {}).get("merged",
                                                                                                             False):
                contribution_score[repo_name] += weights[event_type] / 2
            else:
                contribution_score[repo_name] += weights[event_type]

    # 为没有事件记录的仓库分配最低贡献度
    for repo in contribution_score:
        if contribution_score[repo] == 0:
            contribution_score[repo] = 0.1  # 最低贡献分数

    # 根据贡献分数返回贡献度评价
    contribution_evaluation = {}
    for repo, score in contribution_score.items():
        if score >= 1.5:
            evaluation = 3
        elif score >= 0.5:
            evaluation = 2
        else:
            evaluation = 1
        contribution_evaluation[repo] = evaluation

    return contribution_evaluation


def evaluate_combined_influence(repo_star, repo_fork):
    influence_score = repo_star * 0.7 + repo_fork * 0.3
    if influence_score >= 1000:
        return 5
    elif influence_score >= 500:
        return 4
    elif influence_score >= 100:
        return 3
    elif influence_score >= 10:
        return 2
    else:
        return 1


def evaluate_overall_contribution(contributed_repos):
    """
    根据仓库的影响力和贡献分数对用户的总体贡献进行评价。
    """
    total_score = 0
    total_weight = 0

    # 遍历所有仓库，计算加权贡献分数
    for repo in contributed_repos:
        repo_influence_score = repo["repo_influence"]
        contribution_score = repo["contribution"]

        # 设定权重：假设影响力和贡献度各占一半
        weighted_score = (repo_influence_score * 0.5) + (contribution_score * 0.5)
        total_score += weighted_score
        total_weight += 1

    # 计算平均贡献分数
    # average_score = total_score / total_weight if total_weight > 0 else 0

    return total_score


def get_user_contributed_repos(username):
    """
    获取用户每个贡献过的仓库的资料，包括仓库的名称、star 数、仓库地址和贡献分数。
    """

    contributed_repos = []  # 存储符合条件的仓库信息
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

        # 计算贡献分数
        contribution_scores = calculate_contribution_score(events)

        # 遍历用户的活动，统计每个仓库的事件
        for event in events:
            repo_name = event["repo"]["name"]  # 获取仓库名称

            # 检查是否已记录该仓库
            if not any(repo["repo_name"] == repo_name for repo in contributed_repos):
                # 获取仓库的 star 数和 URL
                repo_url = f"https://api.github.com/repos/{repo_name}"
                repo_response = requests.get(repo_url, headers=headers)
                if repo_response.status_code == 200:
                    repo_data = repo_response.json()
                    repo_star = repo_data.get("stargazers_count", 0)
                    repo_fork = repo_data.get("forks_count", 0)

                    contributed_repos.append({
                        "repo_name": repo_name,
                        "repo_star": repo_star,
                        "repo_influence": evaluate_combined_influence(repo_star, repo_fork),
                        "repo_url": repo_data.get("html_url", ""),
                        "contribution": contribution_scores.get(repo_name, 0)
                    })
                else:
                    print(f"请求仓库详情失败，状态码: {repo_response.status_code}，仓库: {repo_name}")

        page += 1

    return contributed_repos


def get_user_followers_and_following(username):
    """
    获取指定用户的关注者数和关注中数，并返回加权后的 DataFrame。
    """
    data = {
        "用户名": username,
        "关注者数": 0,
        "关注中数": 0,
    }

    # 获取关注中数
    following_url = f"https://api.github.com/users/{username}/following"
    following_response = requests.get(following_url, headers=headers)

    if following_response.status_code == 200:
        following_data = following_response.json()
        following_count = len(following_data)
        data["关注中数"] = following_count
    else:
        print(f"请求关注中列表失败，状态码: {following_response.status_code}，用户: {username}")

    # 获取关注者数
    followers_url = f"https://api.github.com/users/{username}/followers"
    followers_response = requests.get(followers_url, headers=headers)

    if followers_response.status_code == 200:
        followers_data = followers_response.json()
        followers_count = len(followers_data)
        data["关注者数"] = followers_count
    else:
        print(f"请求关注者列表失败，状态码: {followers_response.status_code}，用户: {username}")

    return data


def get_user_repos(username):
    """
    获取用户的仓库信息（包括用户作为 Owner 和 Member 的仓库），并统计总的 Star 数和 Fork 数
    """


    repos = []
    total_stars = 0
    total_forks = 0

    # 遍历仓库类型（Owner 和 Member）
    for repo_type in ["owner", "member"]:
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
                star_count = repo.get("stargazers_count", 0)
                fork_count = repo.get("forks_count", 0)
                total_stars += star_count
                total_forks += fork_count

                repos.append({
                    "repo_name": repo.get("name"),
                    "repo_description": repo.get("description"),
                    "Star": star_count,
                    "Fork": fork_count,
                    "repo_type": repo_type
                })

            page += 1

    # 将仓库信息转换为 DataFrame
    # df_repos = pd.DataFrame(repos)

    return repos


def calculate_talent_rank(total_stars, followers, contribution_score):
    # 定义权重
    total_stars_weight = 0.4
    followers_weight = 0.3
    contribution_score_weight = 0.3

    # 计算 TalentRank_score
    TalentRank_score = (
            total_stars * total_stars_weight +
            followers * followers_weight +
            contribution_score * contribution_score_weight
    )
    return int(TalentRank_score)


def search_repositories_by_language_and_topic(language, topic, max_results=10):
    """
    使用 GitHub 搜索 API 组合搜索项目，按编程语言和主题标签筛选，
    并只返回个人用户创建的项目。分页获取最多 max_results 条结果。
    """


    # 每页获取 100 个结果
    per_page = 100
    pages = (max_results // per_page) + (1 if max_results % per_page > 0 else 0)

    # 创建一个空列表来存储所有符合条件的个人用户项目的信息
    profiles = []

    for page in range(1, pages + 1):
        # 构建搜索查询
        query = f"language:{language}+topic:{topic}"
        url = f"https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repositories = response.json().get('items', [])
            for repo in repositories:
                # 筛选出个人用户创建的项目
                if repo['owner'].get("type") == "User":
                    profiles.append(repo['owner'].get("login"))
                    # profile = {
                    #     "用户名": repo['owner'].get("login"),
                    #     # "项目名": repo.get("name"),
                    #     # "项目主页": repo.get('html_url'),
                    # }
                    # 将每个项目的信息添加到列表中
                    # profiles.append(profile)

                    # 如果达到了 max_results，停止添加
                    if len(profiles) >= max_results:
                        break
            # 如果达到了 max_results，停止分页
            if len(profiles) >= max_results:
                break
        else:
            print(f"请求失败，状态码: {response.status_code}")
            break

    return profiles

