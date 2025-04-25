import streamlit as st
import pandas as pd
from generate_mec import generate_mec_xml_from_dataframe, is_valid_xml_structure

st.set_page_config(page_title="CSV → MEC XML 변환기", page_icon="🎬", layout="centered")

# ---------- 헤더 ----------
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🎬 MEC Metadata Generator</h1>
    <p style='text-align: center; font-size: 16px;'>Amazon Prime Video용 MEC 메타데이터를 쉽고 정확하게 생성하세요.</p>
    <hr>
""", unsafe_allow_html=True)

# ---------- CSV 업로드 ----------
uploaded_file = st.file_uploader("📁 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ {len(df)}개의 언어 행 로딩 완료!")

    # ---------- XML 생성 ----------
    xml = generate_mec_xml_from_dataframe(df)

    # ---------- 유효성 검사 ----------
    is_valid = is_valid_xml_structure(xml)
    if is_valid:
        st.success("✅ XML 구조 유효성 검사 통과!")
    else:
        st.error("❌ XML 구조 오류 발생! 다운로드 전에 확인이 필요합니다.")

    # ---------- 미리보기 ----------
    with st.expander("🔍 XML 내용 미리보기", expanded=True):
        st.code(xml, language="xml")

    # ---------- 다운로드 ----------
    if is_valid:
        st.download_button(
            label="📥 MEC XML 다운로드",
            data=xml,
            file_name="MEC_Metadata.xml",
            mime="application/xml"
        )

# ---------- 제작자 서명 ----------
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: 20px; color: gray; margin-top: 30px;'>
        Made with ❤️ by <strong>EncodingHouse Team</strong>
    </div>
""", unsafe_allow_html=True)
