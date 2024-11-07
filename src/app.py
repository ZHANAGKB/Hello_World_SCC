import pandas as pd
import streamlit as st

from Utility import (get_user_repos, get_user_contributed_repos, get_user_total_stars,
                     get_user_followers_and_following, get_user_profile_nation_detect,
                     evaluate_overall_contribution, calculate_talent_rank,
                     search_repositories_by_language_and_topic)

# 开发者数据
developers = []
contribution = []
# 模拟标准的国家/地区选项
nation_options = [
    "All", "China", "United States", "Canada", "United Kingdom", "Germany",
    "France", "Japan", "South Korea", "India", "Brazil", "Australia",
    "Russia", "South Africa", "Italy", "Spain", "Mexico"
]

# 主页面布局
st.title("DeveloperRank")

# 切换搜索方式
search_mode = st.radio(
    "选择搜索方式",
    ("基于用户名搜索", "基于领域搜索")
)
# 检查 session state 中是否有 offset 和查询条件，如果没有则初始化
if "offset" not in st.session_state:
    st.session_state.offset = 0

if "language_query" not in st.session_state:
    st.session_state.language_query = ""

if "topic_query" not in st.session_state:
    st.session_state.topic_query = ""

if search_mode == "基于用户名搜索":
    # 用户名搜索
    user_name = st.text_input("输入开发者用户名")
    search_button = st.button("搜索")

    # 进行基于用户名的搜索
    if search_button:
        if user_name is not None:
            developer_data = get_user_profile_nation_detect(user_name)
            user_repo = get_user_repos(user_name)
            contribution_data = get_user_contributed_repos(user_name)
            contribution_score = evaluate_overall_contribution(contribution_data)
            total_stars = get_user_total_stars(user_name)
            TalentRank_score = calculate_talent_rank(total_stars, developer_data['关注者数'], contribution_score)

            if developer_data:
                developers.append(developer_data)

                # 开发者展示卡片
                st.subheader("开发者列表")
                for i, dev in enumerate(developers):
                    # 使用expander实现详细信息展开
                    with st.expander(f"{dev['用户名']}"):
                        st.write("**GitHub主页:**")
                        st.write(f"{dev['GitHub 个人主页']}")
                        st.write("**个人简介:**")
                        st.write(f"全名: {dev['全名']}")
                        st.write(f"国家: {dev['国家']}")
                        st.write(f"邮箱: {dev['邮箱']}")
                        st.write("**个人成就:**")
                        st.write(f"个人获得的star: {total_stars}")
                        if user_repo:
                            st.write("**个人项目:**")
                            user_repo_df = pd.DataFrame(user_repo)
                            st.table(user_repo_df)

                        if contribution_data:
                            st.write("**参与的项目:**")
                            repo_df = pd.DataFrame(contribution_data)
                            repo_df = repo_df[["repo_name", "repo_star", "repo_url"]]  # 显示相关字段
                            st.table(repo_df)
                        st.write("**TalentRank 评分:**")
                        st.write(f"{TalentRank_score}")
                        st.write("**社交:**")
                        st.write(f"粉丝数: {developer_data['关注者数']}")

            # 没有找到匹配的开发者时显示提示
            if not developer_data:
                st.write("未找到匹配的开发者。")
    else:
        st.write("点击“搜索”按钮查看开发者列表。")

# 基于领域和 Nation 的搜索页面
elif search_mode == "基于领域搜索":
    # 输入框，存储查询条件
    st.session_state.language_query = st.text_input("输入 language", st.session_state.language_query)
    st.session_state.topic_query = st.text_input("输入 topic", st.session_state.topic_query)
    search_button = st.button("搜索")

    # 增加排序选项
    sort_by_talent_rank = st.checkbox("按 TalentRank 评分排序", value=True)

    # 进行基于领域和 Nation 的搜索
    if search_button:
        print(st.session_state.offset)
        # 获取用户列表
        usernames = search_repositories_by_language_and_topic(
            st.session_state.language_query,
            st.session_state.topic_query,
            max_results=100,
        )
        print(usernames[st.session_state.offset: st.session_state.offset + 5])

        if usernames:
            developers = []  # 重置 developers 列表
            for username in usernames[st.session_state.offset: st.session_state.offset + 5]:
                developer_data = get_user_profile_nation_detect(username)
                user_repo = get_user_repos(username)
                developer_data["user_repo"] = user_repo
                contribution_data = get_user_contributed_repos(username)
                developer_data["contribution_data"] = contribution_data
                contribution_score = evaluate_overall_contribution(contribution_data)
                total_stars = get_user_total_stars(username)
                developer_data["total_stars"] = total_stars

                # 计算 TalentRank_score
                TalentRank_score = calculate_talent_rank(total_stars, developer_data['关注者数'], contribution_score)
                developer_data["TalentRank_score"] = TalentRank_score
                developers.append(developer_data)

            # 按 TalentRank_score 排序（降序）
            if sort_by_talent_rank:
                developers.sort(key=lambda x: x["TalentRank_score"], reverse=True)

            # 开发者展示卡片
            st.subheader("开发者列表")
            for i, dev in enumerate(developers):
                with st.expander(f"{dev['用户名']}"):
                    st.write("**GitHub主页:**")
                    st.write(f"{dev['GitHub 个人主页']}")
                    st.write("**个人简介:**")
                    st.write(f"全名: {dev['全名']}")
                    st.write(f"国家: {dev['国家']}")
                    st.write(f"邮箱: {dev['邮箱']}")
                    st.write("**个人成就:**")
                    st.write(f"个人获得的 star: {dev['total_stars']}")
                    if dev["user_repo"]:
                        st.write("**个人项目:**")
                        user_repo_df = pd.DataFrame(dev["user_repo"])
                        st.table(user_repo_df)

                    # 显示贡献的项目表格
                    if dev['contribution_data']:
                        st.write("**参与的项目:**")
                        repo_df = pd.DataFrame(dev['contribution_data'])
                        repo_df = repo_df[["repo_name", "repo_star", "repo_url"]]
                        st.table(repo_df)

                    st.write("**TalentRank 评分:**")
                    st.write(f"{dev['TalentRank_score']}")
                    st.write("**社交:**")
                    st.write(f"粉丝数: {dev['关注者数']}")

            st.session_state.offset += 5
        else:
            st.write("未找到匹配的开发者。")
    else:
        st.write("点击“搜索”按钮查看开发者列表。")
