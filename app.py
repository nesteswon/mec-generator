# ------------------------------------------------------------------------------
# Copyright (c) 2024 EncodingHouse Team. All Rights Reserved.
#
# 본 소스코드는 EncodingHouse Team의 독점 자산입니다.
# 사전 서면 허가 없이 복제, 수정, 배포, 공개 또는 상업적 이용을 엄격히 금지합니다.
#
# Unauthorized copying, modification, distribution, publication, or commercial use
# of this file is strictly prohibited without prior written consent from EncodingHouse Team.
# ------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from generate_mec import generate_mec_xml_from_dataframe, is_valid_xml_structure

# ---------- 페이지 설정 ----------
st.set_page_config(page_title="MEC Generator", page_icon="🎬", layout="centered")

# ---------- 테마 상태 기억 및 토글 ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("## 🎬 MEC Metadata Generator")
with col2:
    mode_label = "🌞 Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    st.button(mode_label, on_click=toggle_theme)

if st.session_state.dark_mode:
    st.markdown("""
        <style>
        /* 전체 다크모드 배경과 텍스트 */
        body, .stApp {
            background-color: #0f171e;
            color: #ffffff;
        }

        .stMarkdown, .stText, .stHeader, .stSubheader, .stCaption,
        .stDataFrame, .stTable, .stAlert, label, p, h1, h2, h3, h4, h5, h6,
        .css-1d391kg, .css-1cpxqw2 {
            color: #ffffff !important;
        }

        .stButton>button {
            background-color: #0f79af;
            color: #ffffff;
            font-weight: bold;
        }

        .stFileUploader, .stTextInput, .stTextArea, .stSelectbox,
        .stRadio > div, .stExpanderHeader {
            background-color: #1c1f26;
            color: #ffffff;
        }

                /* 다운로드 버튼 스타일 */
        .stDownloadButton > button {
            background-color: #ffffff !important;
            color: #000000 !important;
            font-weight: bold !important;
            border: 1px solid #888 !important;
            transition: background-color 0.3s, color 0.3s;
        }

        /* Hover 시 반전 효과 */
        .stDownloadButton > button:hover {
            background-color: #0f79af !important;
            color: #ffffff !important;
            border: 1px solid #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)


else:
    st.markdown("""
        <style>
        body, .stApp { background-color: #ffffff; color: black; }
        .stButton>button { background-color: #1a98ff; color: white; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

# ---------- 함수 정의 ----------
def validate_summary_length(df):
    errors = []
    for i, row in df.iterrows():
        s190 = str(row.get("Summary190", ""))
        s400 = str(row.get("Summary400", ""))
        if len(s190) > 190:
            errors.append((i + 2, "Summary190", len(s190)))
        if len(s400) > 400:
            errors.append((i + 2, "Summary400", len(s400)))
    return errors

def notify_slack_of_xml_error(error_message, filename="(알 수 없음)"):
    webhook_url = "https://hooks.slack.com/services/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"
    payload = {"text": f"*MEC XML 유효성 검사 실패!*\n📄 파일명: `{filename}`\n```{error_message}```"}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            st.warning(f"Slack 전송 실패: {response.text}")
    except Exception as e:
        st.warning(f"Slack 알림 실패: {e}")

def extract_paths(xml_string):
    try:
        root = ET.fromstring(xml_string)
        paths = set()
        def recurse(node, path=""):
            current = f"{path}/{node.tag}"
            paths.add(current)
            for child in node:
                recurse(child, current)
        recurse(root)
        return paths, ""
    except ET.ParseError as e:
        return set(), f"Parse Error: {e}"

def load_sample_xml(name):
    try:
        with open(name, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

sample_library = {
    "Movie": load_sample_xml("Movie.xml"),
    "Series": load_sample_xml("Series.xml"),
    "Episode": load_sample_xml("Episode.xml")
}

# ---------- 탭 구성 ----------
tab1, tab2 = st.tabs(["📄 MEC XML 생성", "🧩 2nd. Checkpoint"])

generated_xml = None

# ---------- 탭 1: MEC 생성 ----------
with tab1:
    st.markdown("""<h4>CSV 업로드 후 XML 생성</h4>""", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요", type=["csv"])

    if uploaded_file:
        filename = uploaded_file.name
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ {len(df)}개의 언어 행 로딩 완료!")

        summary_errors = validate_summary_length(df)
        if summary_errors:
            st.error(f"❌ Summary 글자 수 제한 초과 항목 발견 ({len(summary_errors)}건)")
            st.dataframe(pd.DataFrame(summary_errors, columns=["행 번호", "컬럼명", "글자수"]))
            notify_slack_of_xml_error("Summary 글자 수 초과", filename)
            st.stop()

        generated_xml = generate_mec_xml_from_dataframe(df)

        if is_valid_xml_structure(generated_xml):
            st.success("✅ XML 구조 유효성 검사 통과!")
        else:
            st.error("❌ XML 구조 오류 발생! 다운로드 전에 확인이 필요합니다.")
            notify_slack_of_xml_error("XML 구조 오류", filename)

        with st.expander("🔍 XML 내용 미리보기", expanded=True):
            st.code(generated_xml, language="xml")

        st.download_button(
            label="📥 MEC XML 다운로드",
            data=generated_xml,
            file_name="MEC_Metadata.xml",
            mime="application/xml"
        )

# ---------- 탭 2: 구조 비교 ----------
with tab2:
    st.markdown("""<h4>2nd. Checkpoint</h4>""", unsafe_allow_html=True)
    selected_sample = st.radio("MEC 종류를 선택하세요:", list(sample_library.keys()), horizontal=True)
    sample_xml = sample_library.get(selected_sample)

    if sample_xml and generated_xml:
        sample_paths, err1 = extract_paths(sample_xml)
        generated_paths, err2 = extract_paths(generated_xml)

        if err1 or err2:
            st.error(f"XML 파싱 오류\n샘플: {err1}\n생성: {err2}")
        else:
            missing = sorted(sample_paths - generated_paths)
            extra = sorted(generated_paths - sample_paths)

            if not missing and not extra:
                st.success("🎉 XML 구조가 완전히 일치합니다!")
            else:
                if missing:
                    st.warning("🔻 생성 XML에 누락된 태그 경로:")
                    st.code("\n".join(missing))
                if extra:
                    st.info("🔺 생성 XML에 추가된 태그 경로:")
                    st.code("\n".join(extra))
    elif not generated_xml:
        st.info("📄 먼저 'MEC XML 생성' 탭에서 CSV를 업로드해주세요.")

# ---------- 푸터 ----------
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: rgba(0,0,0,0.7);
    color: white;
    text-align: center;
    padding: 12px;
    font-size: 13px;
    font-family: 'Helvetica Neue', sans-serif;
    z-index: 100;
}
</style>
<div class="footer">
    Made with ❤️ by <strong>Encodinghouse Team</strong><br>
    © 2024 EncodingHouse Team. Unauthorized use is prohibited.
</div>
""", unsafe_allow_html=True)
