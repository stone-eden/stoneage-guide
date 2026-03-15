import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import random
import base64
import mimetypes
import re

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

    pet_default_columns = {
        "pet_name": "",
        "role": "",
        "raid_rating": 3,
        "earth": 0,
        "water": 0,
        "fire": 0,
        "wind": 0,
        "passive_skill": "",
        "active_skill": "",
        "recommended_skill": "",
        "beginner_friendly": "",
        "notes": "",
        "pre_hp": 0,
        "pre_attack": 0,
        "pre_defense": 0,
        "pre_agility": 0,
        "pre_max_total": 0,
        "post_hp": 0,
        "post_attack": 0,
        "post_defense": 0,
        "post_agility": 0,
        "post_total": 0,
    }

    for col, default in pet_default_columns.items():
        if col not in pets.columns:
            pets[col] = default

    if "main_skill" in pets.columns:
        pets["passive_skill"] = pets["passive_skill"].replace("", pd.NA).fillna(pets["main_skill"])

    if "sub_skill" in pets.columns:
        pets["active_skill"] = pets["active_skill"].replace("", pd.NA).fillna(pets["sub_skill"])

    pet_numeric_cols = [
        "raid_rating",
        "earth", "water", "fire", "wind",
        "pre_hp", "pre_attack", "pre_defense", "pre_agility", "pre_max_total",
        "post_hp", "post_attack", "post_defense", "post_agility", "post_total"
    ]

    for col in pet_numeric_cols:
        pets[col] = pd.to_numeric(pets[col], errors="coerce").fillna(0)

    pets["raid_rating"] = pets["raid_rating"].astype(int)

    pets["pre_current_total"] = (
        pets["pre_hp"] +
        pets["pre_attack"] +
        pets["pre_defense"] +
        pets["pre_agility"]
    ).round(3)

    pets["rainbow_required_total"] = (pets["pre_max_total"] * 0.981).round(3)

    return pets, raids, raid_info, ride_pet


pets_df, raids_df, raid_info_df, ride_pet_df = load_data()


# ---------- 환생 시뮬레이터 설정 ----------
REINCARNATION_MIN_RATIO = 1.15
REINCARNATION_MAX_RATIO = 1.40
DEFAULT_SIM_INPUT_RATIO = 0.981
JACKPOT_GAIN = 1.900


# ---------- 스타일 ----------
st.markdown("""
<style>
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
    max-width: 1200px;
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
    word-break: keep-all;
}

.pet-sub-desc {
    font-size: 15px;
    color: #4b5563;
    margin-top: 16px;
    margin-bottom: 10px;
    line-height: 1.6;
    word-break: keep-all;
    overflow-wrap: break-word;
}

.info-line {
    font-size: 15px;
    margin-bottom: 6px;
    line-height: 1.6;
    color: #1f2937;
    word-break: keep-all;
    overflow-wrap: break-word;
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
    word-break: keep-all;
    overflow-wrap: break-word;
}

.element-block-top {
    margin-top: 16px;
    max-width: 430px;
}

.element-title-inline {
    font-size: 16px;
    font-weight: 800;
    color: #1f2d3d;
    margin-bottom: 10px;
}

.element-row {
    display: flex;
    align-items: center;
    margin: 8px 0;
    gap: 10px;
}

.element-label {
    width: 42px;
    font-weight: 700;
    font-size: 14px;
    color: #374151;
    flex-shrink: 0;
}

.element-bar-wrap {
    flex: 1;
    background: #eceff3;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    max-width: 260px;
}

.element-bar {
    height: 10px;
    border-radius: 999px;
}

.element-value {
    width: 20px;
    text-align: right;
    font-weight: 700;
    font-size: 13px;
    color: #374151;
    flex-shrink: 0;
}

.stat-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 230px;
}

.stat-title {
    font-size: 17px;
    font-weight: 800;
    margin-bottom: 12px;
    color: #111827;
}

.stat-row-basic {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
    gap: 10px;
}

.stat-row-basic:last-child {
    border-bottom: none;
}

.stat-label {
    color: #374151;
    font-weight: 600;
}

.stat-value {
    color: #111827;
    font-weight: 700;
    text-align: right;
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
    min-height: 230px;
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
    word-break: keep-all;
    overflow-wrap: break-word;
}

.rainbow-value {
    font-size: 30px;
    font-weight: 900;
    color: #d97706;
    margin-top: 18px;
}

.summary-card {
    padding: 16px 18px;
    border-radius: 18px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 250px;
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

.skill-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    min-height: 230px;
    height: 230px;
}

.skill-title {
    font-size: 17px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 12px;
}

.skill-row {
    margin-bottom: 12px;
}

.skill-label {
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 4px;
}

.skill-value {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
    line-height: 1.6;
    word-break: keep-all;
    overflow-wrap: break-word;
}

.usage-card {
    padding: 10px 2px 4px 2px;
}

.result-box {
    padding: 14px 16px;
    border-radius: 14px;
    background: #fff8ef;
    border: 1px solid #f4d7b5;
    margin-bottom: 12px;
}

.result-title {
    font-size: 16px;
    font-weight: 800;
    color: #92400e;
    margin-bottom: 10px;
}

.grade-general {
    padding: 16px 18px;
    border-radius: 14px;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    font-size: 20px;
    font-weight: 800;
    color: #374151;
    text-align: center;
}

.grade-rare {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, #f2d06b, #c6902f);
    border: 2px solid #8c6323;
    font-size: 22px;
    font-weight: 900;
    color: #fff8e7;
    text-align: center;
    box-shadow: 0 8px 20px rgba(166, 118, 35, 0.22);
}

.grade-epic {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, #d9534f, #b7282f);
    border: 2px solid #7f1d1d;
    font-size: 24px;
    font-weight: 900;
    color: #fff4f4;
    text-align: center;
    box-shadow: 0 8px 20px rgba(183, 40, 47, 0.24);
}

.grade-near-rainbow {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, #f59e0b, #ef4444, #8b5cf6);
    border: 2px solid #7c3aed;
    font-size: 24px;
    font-weight: 900;
    color: white;
    text-align: center;
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.24);
}

.grade-rainbow {
    padding: 18px 20px;
    border-radius: 16px;
    background: linear-gradient(90deg, #f6c453 0%, #ef4444 35%, #8b5cf6 68%, #60a5fa 100%);
    border: 2px solid #d97706;
    font-size: 28px;
    font-weight: 900;
    color: #fffdf5;
    text-align: center;
    box-shadow: 0 10px 26px rgba(217, 119, 6, 0.28);
}

.jackpot-box {
    padding: 14px 16px;
    border-radius: 14px;
    background: linear-gradient(135deg, #fff7ed, #ffedd5);
    border: 1px solid #fdba74;
    color: #9a3412;
    font-size: 18px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 6px 18px rgba(251, 146, 60, 0.18);
}

.top-html-card {
    min-height: 210px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    background: #ffffff;
    padding: 18px 18px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
}

.top-html-sim {
    min-height: 210px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    background: #ffffff;
    padding: 18px 18px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
}

.top-pet-wrap {
    display: flex;
    align-items: center;
    gap: 18px;
    width: 100%;
}

.top-pet-img {
    width: 140px;
    min-width: 140px;
    height: 140px;
    border-radius: 10px;
    object-fit: contain;
    background: #000;
}

.top-pet-placeholder {
    width: 140px;
    min-width: 140px;
    height: 140px;
    border-radius: 10px;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    font-size: 13px;
    font-weight: 700;
}

.top-pet-info {
    flex: 1;
    min-width: 0;
}

.top-pet-title {
    font-size: 30px;
    font-weight: 900;
    color: #1f2d3d;
    line-height: 1.2;
    margin-bottom: 14px;
    word-break: keep-all;
}

.top-pet-desc {
    font-size: 15px;
    color: #4b5563;
    line-height: 1.7;
    word-break: keep-all;
}

.top-sim-wrap {
    width: 100%;
}

.top-sim-title {
    font-size: 18px;
    font-weight: 900;
    color: #111827;
    margin-bottom: 12px;
}

.top-sim-desc {
    font-size: 14px;
    color: #4b5563;
    line-height: 1.9;
    word-break: keep-all;
}

/* 모바일 대응 */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.2rem;
    }

    .pet-name {
        font-size: 26px;
    }

    .pet-sub-desc,
    .info-line,
    .skill-value,
    .top-pet-desc,
    .top-sim-desc {
        font-size: 14px;
    }

    .summary-card,
    .stat-card,
    .rainbow-card,
    .skill-card {
        min-height: auto;
        height: auto;
    }

    .top-html-card,
    .top-html-sim {
        min-height: auto;
        padding: 14px;
    }

    .top-pet-wrap {
        gap: 12px;
    }

    .top-pet-img,
    .top-pet-placeholder {
        width: 96px;
        min-width: 96px;
        height: 96px;
    }

    .top-pet-title {
        font-size: 22px;
        margin-bottom: 8px;
    }

    .badge {
        font-size: 12px;
        padding: 5px 10px;
    }

    .grade-general,
    .grade-rare,
    .grade-epic,
    .grade-near-rainbow,
    .grade-rainbow {
        font-size: 18px;
        padding: 14px 12px;
    }

    .rainbow-value {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- 공통 함수 ----------
def find_pet_image_path(pet_name):
    candidates = [
        f"images/{pet_name}.gif",
        f"images/{pet_name}.png",
        f"images/{pet_name}.jpg",
        f"images/{pet_name}.jpeg",
        f"images/{pet_name}.webp",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def show_pet_image(pet_name, width=180):
    image_path = find_pet_image_path(pet_name)
    if image_path:
        st.image(image_path, width=width)
    else:
        st.warning("이미지가 없습니다.")


def image_to_base64(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    mime_type = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mime_type};base64,{encoded}"


def get_pet_image_html(pet_name):
    image_path = find_pet_image_path(pet_name)
    if image_path:
        data_uri = image_to_base64(image_path)
        return f'<img src="{data_uri}" class="top-pet-img" alt="{pet_name}">'
    return '<div class="top-pet-placeholder">이미지 없음</div>'


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
    except Exception:
        return "0.000"


def make_star_rating(value):
    try:
        value = int(value)
    except Exception:
        value = 3

    value = max(1, min(5, value))
    full = "⭐" * value
    empty = "☆" * (5 - value)
    return f"{full}{empty}"


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
    return f'<span class="badge badge-default">{role}</span>' if role else ""


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
    return f'<span class="badge badge-default">{level}</span>' if level else ""


def get_difficulty_badge(difficulty):
    difficulty = str(difficulty).strip()
    if difficulty == "쉬움":
        return '<span class="badge badge-easy">쉬움</span>'
    elif difficulty == "보통":
        return '<span class="badge badge-normal">보통</span>'
    elif difficulty == "어려움":
        return '<span class="badge badge-hard">어려움</span>'
    return f'<span class="badge badge-default">{difficulty}</span>' if difficulty else ""


def make_element_row(label, value, color):
    try:
        value = int(float(value))
    except Exception:
        value = 0

    width_percent = max(0, min(value * 10, 100))
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
    try:
        earth = int(float(row.get("earth", 0)))
        water = int(float(row.get("water", 0)))
        fire = int(float(row.get("fire", 0)))
        wind = int(float(row.get("wind", 0)))
    except Exception:
        earth = water = fire = wind = 0

    html = ""

    if earth > 0:
        html += make_element_row("지", earth, "#2ecc71")
    if water > 0:
        html += make_element_row("수", water, "#00cfe8")
    if fire > 0:
        html += make_element_row("화", fire, "#ff4d4f")
    if wind > 0:
        html += make_element_row("풍", wind, "#f1c40f")

    if html == "":
        html = "<div style='color:gray;'>속성 정보 없음</div>"

    return html


def make_stat_card(title, hp, attack, defense, agility, total):
    return f"""
<div class="stat-card">
    <div class="stat-title">{title}</div>
    <div class="stat-row-basic"><span class="stat-label">체력</span><span class="stat-value">{fmt_num(hp)}</span></div>
    <div class="stat-row-basic"><span class="stat-label">공격</span><span class="stat-value">{fmt_num(attack)}</span></div>
    <div class="stat-row-basic"><span class="stat-label">방어</span><span class="stat-value">{fmt_num(defense)}</span></div>
    <div class="stat-row-basic"><span class="stat-label">순발</span><span class="stat-value">{fmt_num(agility)}</span></div>
    <div class="stat-row-basic total-row">
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


def make_summary_card(raid_rating, pre_total, rainbow_total):
    stars = make_star_rating(raid_rating)

    html = '<div class="summary-card">'
    html += '<div class="summary-title">핵심 요약</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">레이드 활용도</div>'
    html += f'<div class="summary-value">{stars}</div>'
    html += '</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">환생 전 총성장</div>'
    html += f'<div class="summary-value">{fmt_num(pre_total)}</div>'
    html += '</div>'

    html += '<div class="summary-section">'
    html += '<div class="summary-label">무지개 기준</div>'
    html += f'<div class="summary-value summary-highlight">{fmt_num(rainbow_total)}</div>'
    html += '</div>'

    html += '</div>'
    return html


def make_skill_card(passive_skill, active_skill, recommended_skill):
    passive_skill = clean_text(passive_skill)
    active_skill = clean_text(active_skill)
    recommended_skill = clean_text(recommended_skill)

    return f"""<div class="skill-card">
<div class="skill-row">
    <div class="skill-label">패시브 스킬</div>
    <div class="skill-value">{passive_skill}</div>
</div>

<div class="skill-row">
    <div class="skill-label">액티브 스킬</div>
    <div class="skill-value">{active_skill}</div>
</div>

<div class="skill-row">
    <div class="skill-label">추천 스킬</div>
    <div class="skill-value">{recommended_skill}</div>
</div>
</div>"""


def calc_total_growth(hp_g, atk_g, def_g, spd_g):
    return round(float(hp_g) + float(atk_g) + float(def_g) + float(spd_g), 3)


def simulate_one_reincarnation(hp_g, atk_g, def_g, spd_g):
    new_hp_g = round(float(hp_g) * random.uniform(REINCARNATION_MIN_RATIO, REINCARNATION_MAX_RATIO), 3)
    new_atk_g = round(float(atk_g) * random.uniform(REINCARNATION_MIN_RATIO, REINCARNATION_MAX_RATIO), 3)
    new_def_g = round(float(def_g) * random.uniform(REINCARNATION_MIN_RATIO, REINCARNATION_MAX_RATIO), 3)
    new_spd_g = round(float(spd_g) * random.uniform(REINCARNATION_MIN_RATIO, REINCARNATION_MAX_RATIO), 3)

    total_g = calc_total_growth(new_hp_g, new_atk_g, new_def_g, new_spd_g)

    return {
        "hp_g": new_hp_g,
        "atk_g": new_atk_g,
        "def_g": new_def_g,
        "spd_g": new_spd_g,
        "total_g": total_g,
    }


def simulate_many_reincarnations(hp_g, atk_g, def_g, spd_g, n=1000):
    return [simulate_one_reincarnation(hp_g, atk_g, def_g, spd_g) for _ in range(n)]


def estimate_post_max_total(current_total, pet_row=None):
    current_total = float(current_total)

    if pet_row is not None:
        pre_max_total = float(pet_row.get("pre_max_total", 0))
        post_total = float(pet_row.get("post_total", 0))

        if pre_max_total > 0 and post_total > 0:
            post_ratio = post_total / pre_max_total
            return round(current_total * post_ratio, 3)

    return round(current_total * REINCARNATION_MAX_RATIO, 3)


def estimate_grade_thresholds(current_total, pet_row=None):
    estimated_post_max_total = estimate_post_max_total(current_total, pet_row)
    rare = round(estimated_post_max_total * 0.82, 3)
    epic = round(estimated_post_max_total * 0.935, 3)
    perfect = round(estimated_post_max_total * 0.988, 3)
    near_rainbow = round(perfect * 0.995, 3)
    return rare, epic, perfect, near_rainbow, estimated_post_max_total


def get_grade(total_g, rare, epic, perfect, near_rainbow):
    total_g = float(total_g)
    if total_g >= perfect:
        return "무지개"
    elif total_g >= near_rainbow:
        return "무지개 근접"
    elif total_g >= epic:
        return "극품"
    elif total_g >= rare:
        return "희귀"
    return "일반"


def get_sim_default_stats(row):
    pre_max_total = float(row.get("pre_max_total", 0))
    pre_hp = float(row.get("pre_hp", 0))
    pre_attack = float(row.get("pre_attack", 0))
    pre_defense = float(row.get("pre_defense", 0))
    pre_agility = float(row.get("pre_agility", 0))

    current_total = pre_hp + pre_attack + pre_defense + pre_agility

    if pre_max_total > 0:
        target_total = round(pre_max_total * DEFAULT_SIM_INPUT_RATIO, 3)
    else:
        target_total = round(current_total, 3)

    if current_total > 0:
        ratio = target_total / current_total
        hp = round(pre_hp * ratio, 3)
        atk = round(pre_attack * ratio, 3)
        defense = round(pre_defense * ratio, 3)
        spd = round(pre_agility * ratio, 3)
    else:
        hp = atk = defense = spd = 0.0

    return hp, atk, defense, spd


def render_sim_top_pet_card(selected_pet):
    image_html = get_pet_image_html(selected_pet)
    return f"""
    <div class="top-html-card">
        <div class="top-pet-wrap">
            {image_html}
            <div class="top-pet-info">
                <div class="top-pet-title">{selected_pet}</div>
                <div class="top-pet-desc">
                    펫을 선택하고 성장치를 입력한 뒤<br>
                    환생 결과를 확인해보세요.
                </div>
            </div>
        </div>
    </div>
    """


def render_sim_top_info_card():
    return """
    <div class="top-html-sim">
        <div class="top-sim-wrap">
            <div class="top-sim-title">환생 시뮬레이터</div>
            <div class="top-sim-desc">
                1회 / 10회<br>
                원하는 방식으로 환생 결과를 확인할 수 있습니다.
            </div>
        </div>
    </div>
    """


def safe_dom_id(text):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", str(text))


def get_grade_theme(grade):
    if grade == "무지개":
        return {
            "badge_bg": "linear-gradient(90deg, #f6c453 0%, #ef4444 35%, #8b5cf6 68%, #60a5fa 100%)",
            "badge_border": "#d97706",
            "badge_color": "#fffdf5",
            "glow": "0 0 24px rgba(246,196,83,0.35)"
        }
    elif grade == "무지개 근접":
        return {
            "badge_bg": "linear-gradient(135deg, #f59e0b, #ef4444, #8b5cf6)",
            "badge_border": "#7c3aed",
            "badge_color": "#ffffff",
            "glow": "0 0 22px rgba(139,92,246,0.28)"
        }
    elif grade == "극품":
        return {
            "badge_bg": "linear-gradient(135deg, #d9534f, #b7282f)",
            "badge_border": "#7f1d1d",
            "badge_color": "#fff4f4",
            "glow": "0 0 18px rgba(217,83,79,0.28)"
        }
    elif grade == "희귀":
        return {
            "badge_bg": "linear-gradient(135deg, #f2d06b, #c6902f)",
            "badge_border": "#8c6323",
            "badge_color": "#fff8e7",
            "glow": "0 0 18px rgba(242,208,107,0.24)"
        }
    else:
        return {
            "badge_bg": "linear-gradient(135deg, #9ca3af, #6b7280)",
            "badge_border": "#4b5563",
            "badge_color": "#ffffff",
            "glow": "0 0 14px rgba(156,163,175,0.2)"
        }


def render_one_reincarnation_result_card(selected_pet, grade, current_stats, result_stats, pet_row=None):
    image_path = find_pet_image_path(selected_pet)
    pet_img = image_to_base64(image_path) if image_path else ""

    hp_now = float(current_stats["hp"])
    atk_now = float(current_stats["atk"])
    def_now = float(current_stats["def"])
    spd_now = float(current_stats["spd"])
    total_now = float(current_stats["total"])

    hp_new = float(result_stats["hp"])
    atk_new = float(result_stats["atk"])
    def_new = float(result_stats["def"])
    spd_new = float(result_stats["spd"])
    total_new = float(result_stats["total"])

    hp_gain = hp_new - hp_now
    atk_gain = atk_new - atk_now
    def_gain = def_new - def_now
    spd_gain = spd_new - spd_now
    total_gain = total_new - total_now

    if pet_row is not None:
        total_bar_max = max(
            total_new,
            total_now,
            float(pet_row.get("post_total", 0)),
            float(pet_row.get("pre_max_total", 0)) * REINCARNATION_MAX_RATIO,
            1.0
        )
        stat_bar_max = max(
            hp_new, atk_new, def_new, spd_new,
            hp_now, atk_now, def_now, spd_now,
            float(pet_row.get("post_hp", 0)),
            float(pet_row.get("post_attack", 0)),
            float(pet_row.get("post_defense", 0)),
            float(pet_row.get("post_agility", 0)),
            1.0
        )
    else:
        total_bar_max = max(total_new, total_now, 1.0)
        stat_bar_max = max(hp_new, atk_new, def_new, spd_new, hp_now, atk_now, def_now, spd_now, 1.0)

    total_start_pct = min((total_now / total_bar_max) * 100, 100)
    hp_start_pct = min((hp_now / stat_bar_max) * 100, 100)
    atk_start_pct = min((atk_now / stat_bar_max) * 100, 100)
    def_start_pct = min((def_now / stat_bar_max) * 100, 100)
    spd_start_pct = min((spd_now / stat_bar_max) * 100, 100)

    total_end_pct = min((total_new / total_bar_max) * 100, 100)
    hp_end_pct = min((hp_new / stat_bar_max) * 100, 100)
    atk_end_pct = min((atk_new / stat_bar_max) * 100, 100)
    def_end_pct = min((def_new / stat_bar_max) * 100, 100)
    spd_end_pct = min((spd_new / stat_bar_max) * 100, 100)

    theme = get_grade_theme(grade)
    uid = safe_dom_id(f"{selected_pet}_{random.randint(1000, 999999)}")

    image_html = (
        f'<img src="{pet_img}" class="rebirth-pet-img" alt="{selected_pet}">'
        if pet_img else
        '<div class="rebirth-pet-placeholder">이미지 없음</div>'
    )

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <style>
        * {{
            box-sizing: border-box;
        }}
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: Pretendard, "Noto Sans KR", Arial, sans-serif;
            color: #ffffff;
            width: 100%;
            overflow-x: hidden;
        }}
        .rebirth-wrap {{
            width: 100%;
            padding: 8px 0 0 0;
        }}
        .rebirth-card {{
            position: relative;
            width: 100%;
            min-height: 540px;
            border-radius: 26px;
            overflow: hidden;
            background:
                radial-gradient(circle at 18% 14%, rgba(255, 190, 80, 0.16), transparent 28%),
                radial-gradient(circle at 78% 18%, rgba(70, 130, 255, 0.10), transparent 22%),
                linear-gradient(180deg, rgba(28, 22, 16, 0.97), rgba(9, 9, 11, 0.99));
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 16px 34px rgba(0,0,0,0.35);
            padding-bottom: 16px;
        }}
        .rebirth-top-glow {{
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 120px;
            background: linear-gradient(180deg, rgba(255,167,38,0.16), rgba(255,167,38,0.02));
            pointer-events: none;
        }}
        .rebirth-title {{
            text-align: center;
            font-size: 42px;
            font-weight: 900;
            color: #ffcc72;
            letter-spacing: 1px;
            padding-top: 20px;
            text-shadow: 0 0 18px rgba(255, 195, 90, 0.22);
        }}
        .rebirth-title span {{
            color: #fff1b2;
            margin-left: 6px;
        }}
        .rebirth-content {{
            display: flex;
            align-items: center;
            gap: 30px;
            padding: 16px 26px 10px 26px;
        }}
        .rebirth-left {{
            width: 32%;
            min-width: 240px;
            text-align: center;
            position: relative;
        }}
        .rebirth-pet-stage {{
            min-height: 265px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .rebirth-pet-stage:before {{
            content: "";
            position: absolute;
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,195,90,0.18), rgba(255,195,90,0.02) 70%);
            filter: blur(4px);
        }}
        .rebirth-pet-img {{
            width: 220px;
            height: 220px;
            object-fit: contain;
            filter: drop-shadow(0 12px 22px rgba(0,0,0,0.45));
            animation: floatPet 2.4s ease-in-out infinite;
            position: relative;
            z-index: 2;
        }}
        .rebirth-pet-placeholder {{
            width: 220px;
            height: 220px;
            border-radius: 18px;
            background: rgba(255,255,255,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #d1d5db;
            font-weight: 700;
            position: relative;
            z-index: 2;
        }}
        @keyframes floatPet {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-8px); }}
            100% {{ transform: translateY(0px); }}
        }}
        .rebirth-grade {{
            display: inline-block;
            padding: 10px 24px;
            border-radius: 999px;
            background: {theme["badge_bg"]};
            border: 2px solid {theme["badge_border"]};
            color: {theme["badge_color"]};
            font-size: 22px;
            font-weight: 900;
            box-shadow: {theme["glow"]};
            opacity: 0;
            transform: translateY(12px) scale(0.95);
            transition: all 0.5s ease;
            max-width: 100%;
            word-break: keep-all;
        }}
        .rebirth-grade.show {{
            opacity: 1;
            transform: translateY(0) scale(1);
        }}
        .rebirth-right {{
            flex: 1;
            min-width: 0;
        }}
        .rebirth-name {{
            font-size: 35px;
            font-weight: 900;
            line-height: 1.2;
            margin-bottom: 8px;
            word-break: keep-all;
        }}
        .rebirth-sub {{
            font-size: 16px;
            color: #e8dcc5;
            font-weight: 700;
            margin-bottom: 14px;
        }}
        .rebirth-line {{
            height: 1px;
            background: linear-gradient(90deg, rgba(255,210,140,0.5), rgba(255,255,255,0.05));
            margin-bottom: 16px;
        }}
        .stat-row {{
            display: grid;
            grid-template-columns: 112px 1fr 88px 90px;
            gap: 14px;
            align-items: center;
            margin: 12px 0;
        }}
        .stat-row.total {{
            margin-bottom: 18px;
        }}
        .stat-label {{
            font-size: 21px;
            font-weight: 900;
            color: #fff6e6;
            word-break: keep-all;
        }}
        .stat-row:not(.total) .stat-label {{
            font-size: 18px;
            font-weight: 800;
        }}
        .bar-track {{
            position: relative;
            height: 18px;
            background: rgba(255,255,255,0.10);
            border-radius: 999px;
            overflow: hidden;
            min-width: 0;
        }}
        .stat-row.total .bar-track {{
            height: 22px;
        }}
        .bar-fill {{
            position: absolute;
            left: 0;
            top: 0;
            border-radius: 999px;
            background: linear-gradient(90deg, #f4a62c 0%, #f7c14a 68%, #59c8ff 100%);
            box-shadow: 0 0 14px rgba(89,200,255,0.22);
            transition: width 2.2s ease-out;
        }}
        .bar-fill.total {{
            background: linear-gradient(90deg, #f0a12b 0%, #f7bf49 50%, #4fb9ff 100%);
        }}
        .stat-value {{
            text-align: right;
            font-size: 20px;
            font-weight: 900;
            color: #ffffff;
            white-space: nowrap;
        }}
        .stat-row:not(.total) .stat-value {{
            font-size: 18px;
        }}
        .stat-gain {{
            text-align: right;
            font-size: 20px;
            font-weight: 900;
            color: #7df071;
            opacity: 0;
            transition: opacity 0.35s ease;
            white-space: nowrap;
        }}
        .stat-gain.show {{
            opacity: 1;
        }}
        .stat-row:not(.total) .stat-gain {{
            font-size: 18px;
        }}
        .tension-text {{
            text-align: center;
            margin-top: 6px;
            color: #f7d28e;
            font-size: 15px;
            font-weight: 800;
            opacity: 0;
            transition: opacity 0.35s ease;
            padding: 0 8px;
        }}
        .tension-text.show {{
            opacity: 1;
        }}
        .bottom-note {{
            margin: 10px 26px 0 26px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.08);
            display: flex;
            justify-content: space-between;
            gap: 16px;
            color: #d4d4d8;
            font-size: 14px;
            flex-wrap: wrap;
        }}
        .bottom-note b {{
            color: #ffffff;
        }}
        .final-total {{
            opacity: 0;
            transform: translateY(6px);
            transition: all 0.4s ease;
        }}
        .final-total.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        @media (max-width: 900px) {{
            .rebirth-title {{
                font-size: 34px;
            }}
            .rebirth-content {{
                gap: 18px;
                padding: 14px 18px 10px 18px;
            }}
            .rebirth-left {{
                min-width: 180px;
            }}
            .rebirth-pet-img,
            .rebirth-pet-placeholder {{
                width: 170px;
                height: 170px;
            }}
            .rebirth-pet-stage {{
                min-height: 200px;
            }}
            .rebirth-name {{
                font-size: 28px;
            }}
            .stat-row {{
                grid-template-columns: 92px 1fr 72px 74px;
                gap: 10px;
            }}
            .stat-label {{
                font-size: 18px;
            }}
            .stat-row:not(.total) .stat-label {{
                font-size: 16px;
            }}
            .stat-value,
            .stat-gain {{
                font-size: 16px;
            }}
            .stat-row:not(.total) .stat-value,
            .stat-row:not(.total) .stat-gain {{
                font-size: 15px;
            }}
        }}

        @media (max-width: 640px) {{
            .rebirth-card {{
                min-height: auto;
                border-radius: 18px;
                padding-bottom: 12px;
            }}
            .rebirth-title {{
                font-size: 26px;
                padding-top: 16px;
            }}
            .rebirth-content {{
                display: block;
                padding: 10px 12px 8px 12px;
            }}
            .rebirth-left {{
                width: 100%;
                min-width: 0;
                margin-bottom: 12px;
            }}
            .rebirth-pet-stage {{
                min-height: 150px;
            }}
            .rebirth-pet-stage:before {{
                width: 120px;
                height: 120px;
            }}
            .rebirth-pet-img,
            .rebirth-pet-placeholder {{
                width: 120px;
                height: 120px;
            }}
            .rebirth-grade {{
                font-size: 16px;
                padding: 8px 16px;
            }}
            .rebirth-name {{
                font-size: 22px;
                text-align: center;
            }}
            .rebirth-sub {{
                font-size: 13px;
                text-align: center;
                margin-bottom: 10px;
            }}
            .rebirth-line {{
                margin-bottom: 10px;
            }}
            .stat-row {{
                grid-template-columns: 78px 1fr 58px 62px;
                gap: 8px;
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 15px;
            }}
            .stat-row:not(.total) .stat-label {{
                font-size: 14px;
            }}
            .bar-track {{
                height: 14px;
            }}
            .stat-row.total .bar-track {{
                height: 18px;
            }}
            .stat-value,
            .stat-gain {{
                font-size: 12px;
            }}
            .stat-row:not(.total) .stat-value,
            .stat-row:not(.total) .stat-gain {{
                font-size: 12px;
            }}
            .tension-text {{
                font-size: 12px;
            }}
            .bottom-note {{
                margin: 8px 12px 0 12px;
                font-size: 12px;
                display: block;
            }}
            .bottom-note > div {{
                margin-bottom: 6px;
                text-align: center;
            }}
        }}
    </style>
    </head>
    <body>
        <div class="rebirth-wrap">
            <div class="rebirth-card">
                <div class="rebirth-top-glow"></div>
                <div class="rebirth-title">환생 성공<span>✦</span></div>

                <div class="rebirth-content">
                    <div class="rebirth-left">
                        <div class="rebirth-pet-stage">
                            {image_html}
                        </div>
                        <div id="{uid}_grade" class="rebirth-grade">{grade}</div>
                        <div id="{uid}_tension" class="tension-text">능력치 상승 확인 중...</div>
                    </div>

                    <div class="rebirth-right">
                        <div class="rebirth-name">{selected_pet}</div>
                        <div class="rebirth-sub">입력 성장치에서 환생 결과까지</div>
                        <div class="rebirth-line"></div>

                        <div class="stat-row total">
                            <div class="stat-label">총성장</div>
                            <div class="bar-track">
                                <div id="{uid}_total" class="bar-fill total" style="width:{total_start_pct:.1f}%; height:100%;"></div>
                            </div>
                            <div id="{uid}_value_total" class="stat-value">0.000</div>
                            <div id="{uid}_gain_total" class="stat-gain">+0.000</div>
                        </div>

                        <div class="stat-row">
                            <div class="stat-label">체력성장</div>
                            <div class="bar-track">
                                <div id="{uid}_hp" class="bar-fill" style="width:{hp_start_pct:.1f}%; height:100%;"></div>
                            </div>
                            <div id="{uid}_value_hp" class="stat-value">0.000</div>
                            <div id="{uid}_gain_hp" class="stat-gain">+0.000</div>
                        </div>

                        <div class="stat-row">
                            <div class="stat-label">공격성장</div>
                            <div class="bar-track">
                                <div id="{uid}_atk" class="bar-fill" style="width:{atk_start_pct:.1f}%; height:100%;"></div>
                            </div>
                            <div id="{uid}_value_atk" class="stat-value">0.000</div>
                            <div id="{uid}_gain_atk" class="stat-gain">+0.000</div>
                        </div>

                        <div class="stat-row">
                            <div class="stat-label">방어성장</div>
                            <div class="bar-track">
                                <div id="{uid}_def" class="bar-fill" style="width:{def_start_pct:.1f}%; height:100%;"></div>
                            </div>
                            <div id="{uid}_value_def" class="stat-value">0.000</div>
                            <div id="{uid}_gain_def" class="stat-gain">+0.000</div>
                        </div>

                        <div class="stat-row">
                            <div class="stat-label">순발성장</div>
                            <div class="bar-track">
                                <div id="{uid}_spd" class="bar-fill" style="width:{spd_start_pct:.1f}%; height:100%;"></div>
                            </div>
                            <div id="{uid}_value_spd" class="stat-value">0.000</div>
                            <div id="{uid}_gain_spd" class="stat-gain">+0.000</div>
                        </div>
                    </div>
                </div>

                <div class="bottom-note">
                    <div>환생 전 총성장 <b>{total_now:.3f}</b></div>
                    <div id="{uid}_final_total" class="final-total">환생 후 총성장 <b>{total_new:.3f}</b></div>
                </div>
            </div>
        </div>

        <script>
        const tension = document.getElementById("{uid}_tension");
        const grade = document.getElementById("{uid}_grade");

        function easeOutCubic(x) {{
            return 1 - Math.pow(1 - x, 3);
        }}

        function animateValue(elementId, startValue, endValue, duration, signed) {{
            const el = document.getElementById(elementId);
            const startTime = performance.now();

            function update(now) {{
                const progress = Math.min((now - startTime) / duration, 1);
                const eased = easeOutCubic(progress);
                const current = startValue + (endValue - startValue) * eased;

                if (signed) {{
                    el.textContent = (current >= 0 ? "+" : "") + current.toFixed(3);
                }} else {{
                    el.textContent = current.toFixed(3);
                }}

                if (progress < 1) {{
                    requestAnimationFrame(update);
                }} else {{
                    if (signed) {{
                        el.textContent = (endValue >= 0 ? "+" : "") + endValue.toFixed(3);
                    }} else {{
                        el.textContent = endValue.toFixed(3);
                    }}
                }}
            }}

            requestAnimationFrame(update);
        }}

        setTimeout(function() {{
            tension.classList.add("show");
        }}, 200);

        setTimeout(function() {{
            document.getElementById("{uid}_total").style.width = "{total_end_pct:.1f}%";
            document.getElementById("{uid}_hp").style.width = "{hp_end_pct:.1f}%";
            document.getElementById("{uid}_atk").style.width = "{atk_end_pct:.1f}%";
            document.getElementById("{uid}_def").style.width = "{def_end_pct:.1f}%";
            document.getElementById("{uid}_spd").style.width = "{spd_end_pct:.1f}%";

            animateValue("{uid}_value_total", 0, {total_new:.3f}, 2200, false);
            animateValue("{uid}_value_hp", 0, {hp_new:.3f}, 2200, false);
            animateValue("{uid}_value_atk", 0, {atk_new:.3f}, 2200, false);
            animateValue("{uid}_value_def", 0, {def_new:.3f}, 2200, false);
            animateValue("{uid}_value_spd", 0, {spd_new:.3f}, 2200, false);

            document.getElementById("{uid}_gain_total").classList.add("show");
            document.getElementById("{uid}_gain_hp").classList.add("show");
            document.getElementById("{uid}_gain_atk").classList.add("show");
            document.getElementById("{uid}_gain_def").classList.add("show");
            document.getElementById("{uid}_gain_spd").classList.add("show");

            animateValue("{uid}_gain_total", 0, {total_gain:.3f}, 2200, true);
            animateValue("{uid}_gain_hp", 0, {hp_gain:.3f}, 2200, true);
            animateValue("{uid}_gain_atk", 0, {atk_gain:.3f}, 2200, true);
            animateValue("{uid}_gain_def", 0, {def_gain:.3f}, 2200, true);
            animateValue("{uid}_gain_spd", 0, {spd_gain:.3f}, 2200, true);
        }}, 450);

        setTimeout(function() {{
            tension.innerText = "최종 등급 판정 중...";
        }}, 2300);

        setTimeout(function() {{
            tension.classList.remove("show");
            grade.classList.add("show");
            document.getElementById("{uid}_final_total").classList.add("show");
        }}, 2950);
        </script>
    </body>
    </html>
    """

    # 모바일에서 iframe 내부가 잘리거나 안 보이는 문제 방지용으로 높이 상향
    components.html(html, height=760, scrolling=False)


def pet_card(pet_name):
    pet_info = pets_df[pets_df["pet_name"] == pet_name]

    if pet_info.empty:
        st.error(f"{pet_name} 정보를 찾을 수 없습니다.")
        return

    row = pet_info.iloc[0]
    raid_rating = row.get("raid_rating", 3)

    passive_skill = row.get("passive_skill", "")
    active_skill = row.get("active_skill", "")
    recommended_skill = row.get("recommended_skill", "")

    with st.container(border=True):
        top1, top2, top3 = st.columns([1.1, 2.2, 1])

        with top1:
            show_pet_image(pet_name, width=180)

        with top2:
            st.markdown(
                f'<div class="pet-name">{clean_text(row.get("pet_name", ""))}</div>',
                unsafe_allow_html=True
            )

            badge_html = get_role_badge(row.get("role", "")) + get_beginner_badge(row.get("beginner_friendly", ""))
            if badge_html.strip():
                st.markdown(badge_html, unsafe_allow_html=True)

            main_desc = clean_text(row.get("notes", ""), "설명 없음")
            st.markdown(
                f'<div class="pet-sub-desc">{main_desc}</div>',
                unsafe_allow_html=True
            )

            st.markdown('<div class="element-block-top">', unsafe_allow_html=True)
            st.markdown('<div class="element-title-inline">속성</div>', unsafe_allow_html=True)
            st.markdown(get_element_graph(row), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with top3:
            st.markdown(
                make_summary_card(
                    raid_rating,
                    row.get("pre_current_total", 0),
                    row.get("rainbow_required_total", 0)
                ),
                unsafe_allow_html=True
            )

        st.markdown('<div class="small-title">핵심 능력치</div>', unsafe_allow_html=True)
        stat1, stat2, stat3 = st.columns(3)

        with stat1:
            st.markdown(
                make_stat_card(
                    "환생 전",
                    row.get("pre_hp", 0),
                    row.get("pre_attack", 0),
                    row.get("pre_defense", 0),
                    row.get("pre_agility", 0),
                    row.get("pre_current_total", 0)
                ),
                unsafe_allow_html=True
            )

        with stat2:
            st.markdown(
                make_stat_card(
                    "환생 후",
                    row.get("post_hp", 0),
                    row.get("post_attack", 0),
                    row.get("post_defense", 0),
                    row.get("post_agility", 0),
                    row.get("post_total", 0)
                ),
                unsafe_allow_html=True
            )

        with stat3:
            st.markdown(
                make_rainbow_card(row.get("rainbow_required_total", 0)),
                unsafe_allow_html=True
            )

        st.markdown('<div class="small-title">스킬 정보</div>', unsafe_allow_html=True)
        skill_col1, skill_col2 = st.columns([2, 1])

        with skill_col1:
            st.markdown(
                make_skill_card(
                    passive_skill,
                    active_skill,
                    recommended_skill
                ),
                unsafe_allow_html=True
            )

        with skill_col2:
            st.markdown(
                """<div class="skill-card">
<div class="skill-title">한줄 체크</div>
<div class="skill-row">
    <div class="skill-label">활용 포인트</div>
    <div class="skill-value">패시브와 액티브 조합, 추천 스킬 세팅을 함께 확인하세요.</div>
</div>
</div>""",
                unsafe_allow_html=True
            )


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

            badge_html = get_recommend_badge(raid_row.get("recommend_level", ""))

            if not pet_info.empty:
                pet_row = pet_info.iloc[0]
                badge_html += get_role_badge(pet_row.get("role", ""))
                badge_html += get_beginner_badge(pet_row.get("beginner_friendly", ""))
                if badge_html.strip():
                    st.markdown(badge_html, unsafe_allow_html=True)

                st.markdown(
                    f'<div class="pet-sub-desc" style="margin-bottom:10px;">{clean_text(pet_row.get("notes", ""), "설명 없음")}</div>',
                    unsafe_allow_html=True
                )

                st.markdown('<div class="small-title" style="font-size:16px;">속성</div>', unsafe_allow_html=True)
                st.markdown(get_element_graph(pet_row), unsafe_allow_html=True)
            else:
                if badge_html.strip():
                    st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown(
                f'<div class="info-line"><span class="info-label">역할:</span> {clean_text(raid_row.get("role_needed", ""))}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="info-line"><span class="info-label">필요 스킬:</span> {clean_text(raid_row.get("required_skill", ""))}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="info-line"><span class="info-label">초보 팁:</span> {clean_text(raid_row.get("beginner_tip", ""))}</div>',
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
        badge = get_difficulty_badge(row.get("difficulty", ""))
        if badge.strip():
            st.markdown(badge, unsafe_allow_html=True)

        st.markdown(f'<div class="raid-info-box"><b>요약:</b> {clean_text(row.get("summary", ""))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>핵심 팁:</b> {clean_text(row.get("core_tip", ""))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>추천 파티:</b> {clean_text(row.get("party_tip", ""))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raid-info-box"><b>주의할 점:</b> {clean_text(row.get("caution", ""))}</div>', unsafe_allow_html=True)

        youtube_url = row.get("youtube_url", "")
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
                st.markdown(f"### {clean_text(row.get('character_role', ''))}")
                st.write(f"**추천 탑승펫:** {clean_text(row.get('ride_pet', ''))}")
                st.write(f"**추천 이유:** {clean_text(row.get('ride_reason', ''))}")

        if i + 1 < len(ride_info):
            with cols[1]:
                with st.container(border=True):
                    row = ride_info.iloc[i + 1]
                    st.markdown(f"### {clean_text(row.get('character_role', ''))}")
                    st.write(f"**추천 탑승펫:** {clean_text(row.get('ride_pet', ''))}")
                    st.write(f"**추천 이유:** {clean_text(row.get('ride_reason', ''))}")


def show_reincarnation_simulator():
    st.header("환생 시뮬레이터")
    st.caption("※ 환생 시뮬레이터는 실제 게임 데이터를 참고한 체감형 기능이며, 참고용으로 활용해주세요.")

    pet_list = sorted(pets_df["pet_name"].dropna().unique().tolist())
    default_pet = "백호" if "백호" in pet_list else pet_list[0]

    selected_pet = st.selectbox(
        "펫 선택",
        pet_list,
        index=pet_list.index(default_pet) if default_pet in pet_list else 0
    )

    pet_info = pets_df[pets_df["pet_name"] == selected_pet]

    default_hp = 0.0
    default_atk = 0.0
    default_def = 0.0
    default_spd = 0.0
    rainbow_required_total = 0.0

    if not pet_info.empty:
        row = pet_info.iloc[0]
        default_hp, default_atk, default_def, default_spd = get_sim_default_stats(row)
        rainbow_required_total = float(row.get("rainbow_required_total", 0))
    else:
        row = None

    top1, top2 = st.columns([1.2, 1])

    with top1:
        st.markdown(render_sim_top_pet_card(selected_pet), unsafe_allow_html=True)

    with top2:
        st.markdown(render_sim_top_info_card(), unsafe_allow_html=True)

    input_col1, input_col2 = st.columns([1, 1])

    with input_col1:
        hp_g = st.number_input("체력 성장", min_value=0.000, value=default_hp, step=0.001, format="%.3f")
        atk_g = st.number_input("공격 성장", min_value=0.000, value=default_atk, step=0.001, format="%.3f")

    with input_col2:
        def_g = st.number_input("방어 성장", min_value=0.000, value=default_def, step=0.001, format="%.3f")
        spd_g = st.number_input("순발 성장", min_value=0.000, value=default_spd, step=0.001, format="%.3f")

    current_total = calc_total_growth(hp_g, atk_g, def_g, spd_g)
    rare_line, epic_line, perfect_line, near_rainbow_line, estimated_post_max_total = estimate_grade_thresholds(current_total, row)

    st.markdown("### 현재 기준")
    cur1, cur2 = st.columns(2)

    with cur1:
        st.metric("현재 총 성장", f"{current_total:.3f}")

    with cur2:
        display_rainbow = rainbow_required_total if rainbow_required_total > 0 else perfect_line
        st.metric("무지개등급 가능 최소 성장치", f"{display_rainbow:.3f}")

    st.markdown("---")

    opt1, opt2 = st.columns([1, 1])

    with opt1:
        sim_count = st.selectbox("시뮬레이션 횟수", [1, 10], index=0)

    with opt2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_sim = st.button("🎲 환생 돌리기", use_container_width=True)

    if run_sim:
        results = simulate_many_reincarnations(hp_g, atk_g, def_g, spd_g, sim_count)

        total_values = [r["total_g"] for r in results]
        avg_total = sum(total_values) / len(total_values)
        min_total = min(total_values)
        max_total = max(total_values)

        best_result = max(results, key=lambda x: x["total_g"])
        worst_result = min(results, key=lambda x: x["total_g"])

        grade_counts = {"일반": 0, "희귀": 0, "극품": 0, "무지개 근접": 0, "무지개": 0}
        for r in results:
            g = get_grade(r["total_g"], rare_line, epic_line, perfect_line, near_rainbow_line)
            grade_counts[g] += 1

        if sim_count == 1:
            one = results[0]
            final_grade = get_grade(one["total_g"], rare_line, epic_line, perfect_line, near_rainbow_line)
            growth_gain = round(one["total_g"] - current_total, 3)

            st.markdown("### 1회 환생 결과")

            render_one_reincarnation_result_card(
                selected_pet=selected_pet,
                grade=final_grade,
                current_stats={
                    "hp": hp_g,
                    "atk": atk_g,
                    "def": def_g,
                    "spd": spd_g,
                    "total": current_total
                },
                result_stats={
                    "hp": one["hp_g"],
                    "atk": one["atk_g"],
                    "def": one["def_g"],
                    "spd": one["spd_g"],
                    "total": one["total_g"]
                },
                pet_row=row
            )

            if growth_gain >= JACKPOT_GAIN:
                st.markdown(
                    f"""
                    <div class="jackpot-box">
                    🚀 초대박 환생! 성장 상승폭 <b>+{growth_gain:.3f}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

           

        else:
            if grade_counts["무지개"] > 0:
                st.markdown(
                    f"""
                    <div class="grade-rainbow">
                    🌈 무지개 등장 {grade_counts["무지개"]}회!!<br>
                    🎉 대박입니다! 🎉
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.balloons()

            elif grade_counts["무지개 근접"] > 0:
                st.markdown(
                    f"""
                    <div class="grade-near-rainbow">
                    ✨ 무지개 근접 {grade_counts["무지개 근접"]}회!<br>
                    정말 아쉽지만 엄청 잘 나왔습니다!
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif grade_counts["극품"] > 0:
                st.markdown(
                    f"""
                    <div class="grade-epic">
                    🔥 극품 환생 {grade_counts["극품"]}회 등장!
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif grade_counts["희귀"] > 0:
                st.markdown(
                    f"""
                    <div class="grade-rare">
                    ✨ 희귀 환생 {grade_counts["희귀"]}회 성공!
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.markdown(
                    """
                    <div class="grade-general">
                    🙂 이번엔 무지개가 나오지 않았습니다
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("### 다회 시뮬레이션 결과")
            r1, r2, r3, r4 = st.columns(4)

            with r1:
                st.metric("평균 총 성장", f"{avg_total:.3f}", f"{avg_total - current_total:+.3f}")
            with r2:
                st.metric("최저 총 성장", f"{min_total:.3f}")
            with r3:
                st.metric("최고 총 성장", f"{max_total:.3f}")
            with r4:
                st.metric("무지개 횟수", f"{grade_counts['무지개']}회")

            g1, g2, g3, g4, g5 = st.columns(5)
            g1.metric("일반", f"{grade_counts['일반']}회")
            g2.metric("희귀", f"{grade_counts['희귀']}회")
            g3.metric("극품", f"{grade_counts['극품']}회")
            g4.metric("근접", f"{grade_counts['무지개 근접']}회")
            g5.metric("무지개", f"{grade_counts['무지개']}회")

            st.markdown("#### 최고 결과")
            st.write(
                f"총 성장 **{best_result['total_g']:.3f}** / "
                f"체력 성장 **{best_result['hp_g']:.3f}**, 공격 성장 **{best_result['atk_g']:.3f}**, "
                f"방어 성장 **{best_result['def_g']:.3f}**, 순발 성장 **{best_result['spd_g']:.3f}**"
            )

            st.markdown("#### 최저 결과")
            st.write(
                f"총 성장 **{worst_result['total_g']:.3f}** / "
                f"체력 성장 **{worst_result['hp_g']:.3f}**, 공격 성장 **{worst_result['atk_g']:.3f}**, "
                f"방어 성장 **{worst_result['def_g']:.3f}**, 순발 성장 **{worst_result['spd_g']:.3f}**"
            )


# ---------- 상단 ----------
st.title("스톤에이지 각성 초보용 펫 도감")
st.caption("레이드별 추천 펫 + 환생 시뮬레이터 통합 Version 2.5 Mobile")

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
    ["레이드별 추천 펫", "펫 도감", "환생 시뮬레이터"]
)


# ---------- 레이드별 추천 펫 ----------
if menu == "레이드별 추천 펫":
    st.header("레이드별 추천 펫")

    raid_list = sorted(raids_df["raid_name"].dropna().unique().tolist())
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

    search_pet = st.text_input(
        "🔍 펫 검색",
        placeholder="예: 루비, 반기노, 노르노르"
    )

    filtered_pets = pets_df.copy()

    if search_pet:
        filtered_pets = filtered_pets[
            filtered_pets["pet_name"].str.contains(search_pet, case=False, na=False)
        ]

    pet_list = sorted(filtered_pets["pet_name"].dropna().unique().tolist())

    if not pet_list:
        st.warning("검색한 펫이 없습니다. 이름을 다시 확인해주세요.")
    else:
        st.caption(f"검색 결과: {len(pet_list)}마리")
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
                        st.markdown(f"### {clean_text(row.get('raid_name', ''))}")
                        st.markdown(f"**추천도:** {clean_text(row.get('recommend_level', ''))}")
                        st.markdown(f"**역할:** {clean_text(row.get('role_needed', ''))}")
                        st.markdown(f"**필요 스킬:** {clean_text(row.get('required_skill', ''))}")
                        st.markdown(f"**초보 팁:** {clean_text(row.get('beginner_tip', ''))}")


# ---------- 환생 시뮬레이터 ----------
elif menu == "환생 시뮬레이터":
    show_reincarnation_simulator()


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