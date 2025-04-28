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
    Made with ❤️ by <strong>Encodinghouse Team</strong>
    Ⓒ 2024 EncodingHouse Team. Unauthorized use is prohibited.
</div>
""", unsafe_allow_html=True)
