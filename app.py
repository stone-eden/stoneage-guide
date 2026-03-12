import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="스톤에이지각성 초보 도감", layout="wide")

# ---------- 데이터 불러오기 ----------
@st.cache_data
def load_data():
    pets = pd.read_csv("pets.csv", encoding="cp949")
    raids = pd.read_csv("raids.csv", encoding="cp949")
    raid_info = pd.read_csv("raid_info.csv", encoding="cp949")
    ride_pet = pd.read_csv("ride_pet.csv", encoding="cp949")

    pets.columns = pets.columns.str.strip()
    raids.columns = raids.columns.str.strip()
    raid_info.columns = raid_info.columns.str.strip()
    ride_pet.columns = ride_pet.columns.str.strip()

    # 숫자 컬럼 처리
    pet_numeric_cols = [
        "earth", "water", "fire", "wind",
        "pre_hp", "pre_attack", "pre_defense", "pre_agility", "pre_max_total",
        "post_hp", "post_attack", "post_defense", "post_agility", "post_total"
    ]

    for col in pet_numeric_cols:
        if col not in pets.columns:
            pets[col] = 0
        pets[col] = pd.to_numeric(pets[col], errors="coerce").fillna(0)

    # raid_rating 컬럼 없으면 기본값 3
    if "raid_rating" not in pets.columns:
        pets["raid_rating"] = 3
    pets["raid_rating"] = pd.to_numeric(pets["raid_rating"], errors="coerce").fillna(3).astype(int)

    # 환생 전 총성장 자동 계산
    pets["pre_current_total"] = (
        pets["pre_hp"] +
        pets["pre_attack"] +
        pets["pre_defense"] +
        pets["pre_agility"]
    ).round(3)

    # 무지개 등급 가능 최소 능력치
    pets["rainbow_required_total"] = (pets["pre_max_total"] * 0.981).round(3)

    return pets, raids, raid_info, ride_pet


pets_df, raids_df, raid_info_df, ride_pet_df = load_data()

# ---------- 스타일 ----------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    margin-right: 8px;
    margin-bottom: 8px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    color: white;
    line-height: 1.2;
}

.badge-dealer { background-color: #e74c3c; }
.badge-tanker { background-color: #3498db; }
.badge-support { background-color: #27ae60; }
.badge-healer { background-color: #9b59b6; }
.badge-beginner { background-color: #f39c12; }
.badge-default { background-color: #7f8c8d; }
.badge-essential { background-color: #8e44ad; }
.badge-recommend { background-color: #16a085; }
.badge-alternative { background-color: #95a5a6; }
.badge-easy { background-color: #2ecc71; }
.badge-normal { background-color: #f1c40f; color: black; }
.badge-hard { background-color: #e74c3c; }

.pet-name {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 10px;
    color: #1f2d3d;
    line-height: 1.2;
}

.pet-sub-desc {
    font-size: 15px;
    color: #4b5563;
    margin-top: 6px;
    margin-bottom: 14px;
    line-height: 1.6;
}

.info-line {
    font-size: 15px;
    margin-bottom: 6px;
    line-height: 1.6;
    color: #1f2937;
}

.info-label {
    font-weight: 700;
}

.small-title {
    font-size: 18px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 10px;
    color: #1f2d3d;
}

.footer-box {
    text-align: center;
    font-size: 14px;
    color: gray;
    padding: 20px 0;
}

.raid-info-box {
    padding: 8px 0 12px 0;
}

.element-row {
    display: flex;
    align-items: center;
    margin: 8px 0;
    gap: 10px;
}

.element-label {
    width: 60px;
    font-weight: 700;
    font-size: 14px;
    color: #374151;
}

.element-bar-wrap {
    flex: 1;
    background: #eceff3;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
}

.element-bar {
    height: 10px;
    border-radius: 999px;
}

.element-value {
    width: 24px;
    text-align: right;
    font-weight: 700;
    font-size: 13px;
    color: #374151;
}

.stat-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 220px;
}

.stat-title {
    font-size: 17px;
    font-weight: 800;
    margin-bottom: 12px;
    color: #111827;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
}

.stat-row:last-child {
    border-bottom: none;
}

.stat-label {
    color: #374151;
    font-weight: 600;
}

.stat-value {
    color: #111827;
    font-weight: 700;
}

.total-row {
    margin-top: 8px;
    padding-top: 10px;
    border-top: 1px solid #dbe2ea;
}

.total-label {
    color: #b45309;
    font-weight: 800;
}

.total-value {
    color: #d97706;
    font-weight: 800;
}

.rainbow-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #fff8ef;
    border: 1px solid #f4d7b5;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.rainbow-title {
    font-size: 17px;
    font-weight: 800;
    color: #92400e;
    margin-bottom: 10px;
}

.rainbow-desc {
    font-size: 14px;
    color: #7c5a2b;
    line-height: 1.6;
}

.rainbow-value {
    font-size: 30px;
    font-weight: 900;
    color: #d97706;
    margin-top: 18px;
}

.summary-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 220px;
}

.summary-title {
    font-size: 17px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 12px;
}

.summary-section {
    margin-bottom: 16px;
}

.summary-label {
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 4px;
}

.summary-value {
    font-size: 16px;
    font-weight: 800;
    color: #111827;
}

.summary-highlight {
    color: #d97706;
}

.usage-card {
    padding: 10px 2px 4px 2px;
}
</style>
""", unsafe_allow_html=True)

# ---------- 공통 함수 ----------
def show_pet_image(pet_name, width=180):
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

def clean_text(value, default="없음"):
    if pd.isna(value):
        return default
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return default
    return text

def fmt_num(value):
    try:
        return f"{float(value):.3f}"
    except:
        return "0.000"

def make_star_rating(value):
    try:
        value = int(value)
    except:
        value = 3

    value = max(1, min(5, value))
    full = "⭐" * value
    empty = "☆" * (5 - value)
    return f"{full}{empty}"

def get_main_element_text(row):
    element_map = [
        ("지속성", row.get("earth", 0)),
        ("수속성", row.get("water", 0)),
        ("화속성", row.get("fire", 0)),
        ("풍속성", row.get("wind", 0)),
    ]

    valid_elements = []
    for name, val in element_map:
        try:
            num = int(float(val))
            if num > 0:
                valid_elements.append((name, num))
        except:
            pass

    if not valid_elements:
        return "속성 없음"

    main_element = max(valid_elements, key=lambda x: x[1])
    return f"{main_element[0]} {main_element[1]}"

def get_role_badge(role):
    role = str(role).strip()
    if role == "딜러":
        return '<span class="badge badge-dealer">딜러</span>'
    elif role == "탱커":
        return '<span class="badge badge-tanker">탱커</span>'
    elif role == "보조":
        return '<span class="badge badge-support">보조</span>'
    elif role == "힐러":
        return '<span class="badge badge-healer">힐러</span>'
    return f'<span class="badge badge-default">{role}</span>'

def get_beginner_badge(beginner_text):
    text = str(beginner_text).strip()
    if text == "예":
        return '<span class="badge badge-beginner">초보 추천</span>'
    elif text == "추천":
        return '<span class="badge badge-beginner">추천</span>'
    return ""

def get_recommend_badge(recommend_level):
    level = str(recommend_level).strip()
    if level == "필수":
        return '<span class="badge badge-essential">필수</span>'
    elif level == "추천":
        return '<span class="badge badge-recommend">추천</span>'
    elif level == "대체":
        return '<span class="badge badge-alternative">대체</span>'
    return f'<span class="badge badge-default">{level}</span>'

def get_difficulty_badge(difficulty):
    difficulty = str(difficulty).strip()
    if difficulty == "쉬움":
        return '<span class="badge badge-easy">쉬움</span>'
    elif difficulty == "보통":
        return '<span class="badge badge-normal">보통</span>'
    elif difficulty == "어려움":
        return '<span class="badge badge-hard">어려움</span>'
    return f'<span class="badge badge-default">{difficulty}</span>'

def make_element_row(label, value, color):
    value = int(value)
    width_percent = value * 10
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

def make_stat_card(title, hp, attack, defense, agility, total):
    return f"""
<div class="stat-card">
    <div class="stat-title">{title}</div>
    <div class="stat-row"><span class="stat-label">체력</span><span class="stat-value">{fmt_num(hp)}</span></div>
    <div class="stat-row"><span class="stat-label">공격</span><span class="stat-value">{fmt_num(attack)}</span></div>
    <div class="stat-row"><span class="stat-label">방어</span><span class="stat-value">{fmt_num(defense)}</span></div>
    <div class="stat-row"><span class="stat-label">순발</span><span class="stat-value">{fmt_num(agility)}</span></div>
    <div class="stat-row total-row">
        <span class="total-label">총성장</span>
        <span class="total-value">{fmt_num(total)}</span>
    </div>
</div>
"""

def make_rainbow_card(required_total):
    return f"""
<div class="rainbow-card">
    <div>
        <div class="rainbow-title">무지개 등급 기준</div>
        <div class="rainbow-desc">
            환생 전 기준으로<br>
            무지개 등급 가능 최소 총능력치
        </div>
    </div>
    <div class="rainbow-value">{fmt_num(required_total)}</div>
</div>
"""

def make_summary_card(raid_rating, main_element_text, pre_total, rainbow_total):
    stars = make_star_rating(raid_rating)

    html = '<div class="summary-card">'
    html += '<div class="summary-title">핵심 요약</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">레이드 활용도</div>'
    html += f'<div class="summary-value">{stars}</div>'
    html += '</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">환생전 총성장</div>'
    html += f'<div class="summary-value">{fmt_num(pre_total)}</div>'
    html += '</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">무지개 기준</div>'
    html += f'<div class="summary-value summary-highlight">{fmt_num(rainbow_total)}</div>'
    html += '</div>'

    html += '</div>'
    return html

def pet_card(pet_name):
    pet_info = pets_df[pets_df["pet_name"] == pet_name]

    if pet_info.empty:
        st.error(f"{pet_name} 정보를 찾을 수 없습니다.")
        return

    row = pet_info.iloc[0]
    raid_rating = row["raid_rating"] if "raid_rating" in row.index else 3
    main_element_text = get_main_element_text(row)

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            show_pet_image(pet_name, width=180)

        with col2:
            st.markdown(
                f'<div class="pet-name">{clean_text(row["pet_name"])}</div>',
                unsafe_allow_html=True
            )

            badge_html = get_role_badge(row["role"]) + get_beginner_badge(row["beginner_friendly"])
            st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown(
                f'<div class="pet-sub-desc">{clean_text(row["notes"], "설명 없음")}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="info-line"><span class="info-label">주요 스킬:</span> {clean_text(row["main_skill"])}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="info-line"><span class="info-label">보조 스킬:</span> {clean_text(row["sub_skill"])}</div>',
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                make_summary_card(
                    raid_rating,
                    main_element_text,
                    row["pre_current_total"],
                    row["rainbow_required_total"]
                ),
                unsafe_allow_html=True
            )

        st.markdown('<div class="small-title">핵심 능력치</div>', unsafe_allow_html=True)
        stat1, stat2, stat3 = st.columns(3)

        with stat1:
            st.markdown(
                make_stat_card(
                    "환생 전",
                    row["pre_hp"],
                    row["pre_attack"],
                    row["pre_defense"],
                    row["pre_agility"],
                    row["pre_current_total"]
                ),
                unsafe_allow_html=True
            )

        with stat2:
            st.markdown(
                make_stat_card(
                    "환생 후",
                    row["post_hp"],
                    row["post_attack"],
                    row["post_defense"],
                    row["post_agility"],
                    row["post_total"]
                ),
                unsafe_allow_html=True
            )

        with stat3:
            st.markdown(
                make_rainbow_card(row["rainbow_required_total"]),
                unsafe_allow_html=True
            )

        st.markdown('<div class="small-title">속성</div>', unsafe_allow_html=True)
        st.markdown(get_element_graph(row), unsafe_allow_html=True)

def raid_pet_card(raid_row):
    pet_name = raid_row["recommended_pet"]
    pet_info = pets_df[pets_df["pet_name"] == pet_name]

    with st.container(border=True):
        st.markdown('<div class="usage-card">', unsafe_allow_html=True)

        col_img, col_info = st.columns([1, 2])

        with col_img:
            show_pet_image(pet_name, width=160)

        with col_info:
            st.markdown(
                f'<div class="pet-name" style="font-size:28px;">{clean_text(pet_name)}</div>',
                unsafe_allow_html=True
            )

            badge_html = get_recommend_badge(raid_row["recommend_level"])

            if not pet_info.empty:
                pet_row = pet_info.iloc[0]
                badge_html += get_role_badge(pet_row["role"])
                badge_html += get_beginner_badge(pet_row["beginner_friendly"])
                st.markdown(badge_html, unsafe_allow_html=True)

                st.markdown(
                    f'<div class="pet-sub-desc" style="margin-bottom:10px;">{clean_text(pet_row["notes"], "설명 없음")}</div>',
                    unsafe_allow_html=True
                )

                st.markdown('<div class="small-title" style="font-size:16px;">속성</div>', unsafe_allow_html=True)
                st.markdown(get_element_graph(pet_row), unsafe_allow_html=True)
            else:
                st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown(
                f'<div class="info-line"><span class="info-label">역할:</span> {clean_text(raid_row["role_needed"])}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="info-line"><span class="info-label">필요 스킬:</span> {clean_text(raid_row["required_skill"])}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="info-line"><span class="info-label">초보 팁:</span> {clean_text(raid_row["beginner_tip"])}</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

def show_raid_info(selected_raid):
    raid_detail = raid_info_df[raid_info_df["raid_name"] == selected_raid]

    if raid_detail.empty:
        st.info("등록된 레이드 설명이 없습니다.")
        return

    row = raid_detail.iloc[0]

    with st.container(border=True):
        st.markdown("## 레이드 설명")
        st.markdown(get_difficulty_badge(row["difficulty"]), unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>요약:</b> {clean_text(row["summary"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>핵심 팁:</b> {clean_text(row["core_tip"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>추천 파티:</b> {clean_text(row["party_tip"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>주의할 점:</b> {clean_text(row["caution"])}</div>', unsafe_allow_html=True)

        youtube_url = ""
        if "youtube_url" in raid_info_df.columns:
            youtube_url = row["youtube_url"]

        if pd.notna(youtube_url) and str(youtube_url).strip() != "":
            st.link_button("🎬 해당 레이드 공략 영상 보기", youtube_url)
        else:
            st.info("등록된 공략 영상이 없습니다.")

def show_ride_pet_info(selected_raid):
    ride_info = ride_pet_df[ride_pet_df["raid_name"] == selected_raid].reset_index(drop=True)

    st.markdown("---")
    st.subheader("캐릭터 역할별 추천 탑승펫")

    if ride_info.empty:
        st.info("등록된 탑승펫 정보가 없습니다.")
        return

    for i in range(0, len(ride_info), 2):
        cols = st.columns(2)

        with cols[0]:
            with st.container(border=True):
                row = ride_info.iloc[i]
                st.markdown(f"### {clean_text(row['character_role'])}")
                st.write(f"**추천 탑승펫:** {clean_text(row['ride_pet'])}")
                st.write(f"**추천 이유:** {clean_text(row['ride_reason'])}")

        if i + 1 < len(ride_info):
            with cols[1]:
                with st.container(border=True):
                    row = ride_info.iloc[i + 1]
                    st.markdown(f"### {clean_text(row['character_role'])}")
                    st.write(f"**추천 탑승펫:** {clean_text(row['ride_pet'])}")
                    st.write(f"**추천 이유:** {clean_text(row['ride_reason'])}")

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

st.link_button(
    "📺 스톤하는 Eden 유튜브",
    "https://www.youtube.com/@스톤하는Eden"
)

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

    show_raid_info(selected_raid)

    st.markdown("---")
    st.subheader(f"{selected_raid} 추천 펫")

    filtered = raids_df[raids_df["raid_name"] == selected_raid].reset_index(drop=True)

    if filtered.empty:
        st.warning("등록된 추천 펫이 없습니다.")
    else:
        for i in range(0, len(filtered), 2):
            cols = st.columns(2)

            with cols[0]:
                raid_pet_card(filtered.iloc[i])

            if i + 1 < len(filtered):
                with cols[1]:
                    raid_pet_card(filtered.iloc[i + 1])

    show_ride_pet_info(selected_raid)

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
                    st.markdown(f"### {clean_text(row['raid_name'])}")
                    st.markdown(f"**추천도:** {clean_text(row['recommend_level'])}")
                    st.markdown(f"**역할:** {clean_text(row['role_needed'])}")
                    st.markdown(f"**필요 스킬:** {clean_text(row['required_skill'])}")
                    st.markdown(f"**초보 팁:** {clean_text(row['beginner_tip'])}")

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