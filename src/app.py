import streamlit as st
from Utility import get_user_profile, get_user_profile_nation_detect

# 开发者数据
developers = []
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
                        st.write("**个人贡献:**")

                        st.write("**社交:**")
                        st.write(f"关注者数: {dev['关注者数']}")
                        st.write(f"他关注中出现最多的国家: {dev['关注中出现最多的国家']}")

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

    else:
        st.write("点击“搜索”按钮查看开发者列表。")
