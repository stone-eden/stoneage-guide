import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="스톤에이지 초보 도감", layout="wide")

# CSV 불러오기
pets_df = pd.read_csv("pets.csv", encoding="cp949")
raids_df = pd.read_csv("raids.csv", encoding="cp949")

# ---------- 스타일 ----------
st.markdown("""
<style>
.badge {
    display: inline-block;
    padding: 6px 12px;
    margin-right: 8px;
    margin-bottom: 8px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: bold;
    color: white;
}
.badge-dealer {
    background-color: #e74c3c;
}
.badge-tanker {
    background-color: #3498db;
}
.badge-support {
    background-color: #27ae60;
}
.badge-beginner {
    background-color: #f39c12;
}
.badge-default {
    background-color: #7f8c8d;
}
.pet-name {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 10px;
}
.desc-box {
    padding: 6px 0;
    font-size: 16px;
}
.element-row {
    display: flex;
    align-items: center;
    margin: 8px 0;
    gap: 10px;
}
.element-label {
    width: 70px;
    font-weight: bold;
}
.element-bar-wrap {
    flex: 1;
    background: #e9ecef;
    border-radius: 999px;
    height: 16px;
    overflow: hidden;
}
.element-bar {
    height: 16px;
    border-radius: 999px;
}
.element-value {
    width: 30px;
    text-align: right;
    font-weight: bold;
}
.footer-box {
    text-align: center;
    font-size: 14px;
    color: gray;
    padding: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------- 공통 함수 ----------
def show_pet_image(pet_name, width=220):
    gif_path = f"images/{pet_name}.gif"
    png_path = f"images/{pet_name}.png"
    jpg_path = f"images/{pet_name}.jpg"
    jpeg_path = f"images/{pet_name}.jpeg"
    webp_path = f"images/{pet_name}.webp"

    if os.path.exists(gif_path):
        st.image(gif_path, width=width)
    elif os.path.exists(png_path):
        st.image(png_path, width=width)
    elif os.path.exists(jpg_path):
        st.image(jpg_path, width=width)
    elif os.path.exists(jpeg_path):
        st.image(jpeg_path, width=width)
    elif os.path.exists(webp_path):
        st.image(webp_path, width=width)
    else:
        st.warning("이미지가 없습니다.")

def get_role_badge(role):
    role = str(role).strip()
    if role == "딜러":
        return '<span class="badge badge-dealer">딜러</span>'
    elif role == "탱커":
        return '<span class="badge badge-tanker">탱커</span>'
    elif role == "보조":
        return '<span class="badge badge-support">보조</span>'
    else:
        return f'<span class="badge badge-default">{role}</span>'

def get_beginner_badge(beginner_text):
    if str(beginner_text).strip() == "예":
        return '<span class="badge badge-beginner">초보 추천</span>'
    return ""

def make_element_row(label, value, color):
    value = int(value)
    width_percent = value * 10  # 총합 10 기준
    return f"""
    <div class="element-row">
        <div class="element-label">{label}</div>
        <div class="element-bar-wrap">
            <div class="element-bar" style="width:{width_percent}%; background:{color};"></div>
        </div>
        <div class="element-value">{value}</div>
    </div>
    """

def get_element_graph(row):
    earth = int(row["earth"])
    water = int(row["water"])
    fire = int(row["fire"])
    wind = int(row["wind"])

    html = ""

    # 0보다 큰 속성만 표시
    if earth > 0:
        html += make_element_row("지속성", earth, "#2ecc71")
    if water > 0:
        html += make_element_row("수속성", water, "#00cfe8")
    if fire > 0:
        html += make_element_row("화속성", fire, "#ff4d4f")
    if wind > 0:
        html += make_element_row("풍속성", wind, "#f1c40f")

    if html == "":
        html = "<div style='color:gray;'>속성 정보 없음</div>"

    return html

def pet_card(pet_name):
    pet_info = pets_df[pets_df["pet_name"] == pet_name]

    if pet_info.empty:
        st.error(f"{pet_name} 정보를 찾을 수 없습니다.")
        return

    row = pet_info.iloc[0]

    with st.container(border=True):
        col1, col2 = st.columns([1, 2])

        with col1:
            show_pet_image(pet_name, width=240)

        with col2:
            st.markdown(f'<div class="pet-name">{row["pet_name"]}</div>', unsafe_allow_html=True)

            badge_html = get_role_badge(row["role"]) + get_beginner_badge(row["beginner_friendly"])
            st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown("### 속성")
            st.markdown(get_element_graph(row), unsafe_allow_html=True)

            st.markdown(
                f'<div class="desc-box"><b>주요 스킬:</b> {row["main_skill"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="desc-box"><b>보조 스킬:</b> {row["sub_skill"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="desc-box"><b>설명:</b> {row["notes"]}</div>',
                unsafe_allow_html=True
            )

def raid_pet_card(raid_row):
    pet_name = raid_row["recommended_pet"]
    pet_info = pets_df[pets_df["pet_name"] == pet_name]

    with st.container(border=True):
        col1, col2 = st.columns([1, 3])

        with col1:
            show_pet_image(pet_name, width=180)

        with col2:
            st.markdown(f'<div class="pet-name">{pet_name}</div>', unsafe_allow_html=True)

            if not pet_info.empty:
                pet_row = pet_info.iloc[0]

                badge_html = get_role_badge(pet_row["role"]) + get_beginner_badge(pet_row["beginner_friendly"])
                st.markdown(badge_html, unsafe_allow_html=True)

                st.markdown("#### 속성")
                st.markdown(get_element_graph(pet_row), unsafe_allow_html=True)

            st.markdown(f'<div class="desc-box"><b>역할:</b> {raid_row["role_needed"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="desc-box"><b>필요 스킬:</b> {raid_row["required_skill"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="desc-box"><b>초보 팁:</b> {raid_row["beginner_tip"]}</div>', unsafe_allow_html=True)

# ---------- 상단 ----------
st.title("스톤에이지 초보용 펫 도감")
st.caption("레이드별 추천 펫과 펫 정보를 카드 형태로 정리한 버전")

st.markdown("""
<div style="padding: 10px 0 20px 0;">
👨‍💻 <b>제작자 : 스톤하는 Eden</b><br>
📺 <a href="https://www.youtube.com/@%EC%8A%A4%ED%86%A4%ED%95%98%EB%8A%94Eden" target="_blank">
유튜브 채널 바로가기
</a>
</div>
""", unsafe_allow_html=True)

# ---------- 메뉴 ----------
menu = st.sidebar.radio(
    "메뉴 선택",
    ["레이드별 추천 펫", "펫 도감"]
)

# ---------- 레이드별 추천 펫 ----------
if menu == "레이드별 추천 펫":
    st.header("레이드별 추천 펫")

    raid_list = sorted(raids_df["raid_name"].unique().tolist())
    selected_raid = st.selectbox("레이드 선택", raid_list)

    filtered = raids_df[raids_df["raid_name"] == selected_raid]

    st.subheader(f"{selected_raid} 추천 펫 카드")

    if filtered.empty:
        st.warning("등록된 추천 펫이 없습니다.")
    else:
        for _, row in filtered.iterrows():
            raid_pet_card(row)

# ---------- 펫 도감 ----------
elif menu == "펫 도감":
    st.header("펫 도감")

    pet_list = sorted(pets_df["pet_name"].unique().tolist())
    selected_pet = st.selectbox("펫 선택", pet_list)

    pet_info = pets_df[pets_df["pet_name"] == selected_pet]

    if not pet_info.empty:
        pet_card(selected_pet)

        st.markdown("---")
        st.subheader("이 펫이 사용되는 레이드")

        related_raids = raids_df[raids_df["recommended_pet"] == selected_pet]

        if related_raids.empty:
            st.info("등록된 레이드 정보가 없습니다.")
        else:
            for _, row in related_raids.iterrows():
                with st.container(border=True):
                    st.markdown(f"### {row['raid_name']}")
                    st.markdown(f"**역할:** {row['role_needed']}")
                    st.markdown(f"**필요 스킬:** {row['required_skill']}")
                    st.markdown(f"**초보 팁:** {row['beginner_tip']}")

# ---------- 하단 ----------
st.markdown("---")
st.markdown("""
<div class="footer-box">
제작자 : <b>스톤하는 Eden</b><br>
유튜브 :
<a href="https://www.youtube.com/@%EC%8A%A4%ED%86%A4%ED%95%98%EB%8A%94Eden" target="_blank">
스톤하는 Eden 채널 바로가기
</a>
</div>
""", unsafe_allow_html=True)