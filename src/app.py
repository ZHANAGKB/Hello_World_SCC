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
    ("基于用户名搜索", "基于领域和 Nation 搜索")
)

if search_mode == "基于用户名搜索":
    # 用户名搜索
    user_name = st.text_input("输入开发者用户名")
    search_button = st.button("搜索")

    # 进行基于用户名的搜索
    if search_button:
        if user_name is not None:
            developer_data = get_user_profile_nation_detect(user_name)
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
                        if contribution_data:
                            st.write("**参与的项目:**")
                            repo_df = pd.DataFrame(contribution_data)
                            repo_df = repo_df[["repo_name", "repo_star", "repo_url", "repo_influence",
                                               "contribution"]]  # 显示相关字段
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

elif search_mode == "基于领域和 Nation 搜索":
    # 基于领域和 Nation 的搜索
    language_query = st.text_input("输入language")
    topic_query = st.text_input("输入topic")
    # nation_filter = st.selectbox("选择 Nation", nation_options)  # 使用标准的国家选项
    search_button = st.button("搜索")

    # 进行基于领域和 Nation 的搜索
    if search_button:
        usernames = search_repositories_by_language_and_topic(language_query, topic_query)
        if usernames:
            for username in usernames:
                developer_data = get_user_profile_nation_detect(username)
                contribution_data = get_user_contributed_repos(username)
                contribution_score = evaluate_overall_contribution(contribution_data)
                total_stars = get_user_total_stars(username)
                TalentRank_score = calculate_talent_rank(total_stars, developer_data['关注者数'], contribution_score)
                developer_data["TalentRank_score"] = TalentRank_score
                developers.append(developer_data)

    else:
        st.write("点击“搜索”按钮查看开发者列表。")
