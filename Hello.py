import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="반갑습니다", 
    initial_sidebar_state="expanded", 
    layout="wide",
    menu_items={})

hide_streamlit_logo = """
    <style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    </style>
"""
st.markdown(hide_streamlit_logo, unsafe_allow_html=True)

st.markdown("# 환영합니다 👋")

st.markdown(
    """
    <br><br>
    GPT 사용법 교육에 오신 여러분을 환영합니다 😀\n
    <br>
    해당 교육 코스는 ChatGPT를 보다 심도깊게 사용하기 위해서 고안된 과정입니다.\n
    ChatGPT 내부에서 ***작동하는 원리***를 하나씩 배워보겠습니다.\n
    나아가 ***더 좋은 질문과 답변을 생성하기 위한 방법***들을 살펴보겠습니다.
    """,
    unsafe_allow_html=True,
)


api_key = st.text_input(
    label="APIKEY",
    placeholder="OpenAI API KEY",
    type="password",
    label_visibility="hidden",
)

api_submit = st.button("로그인", key="submit_apikey")

if api_submit:
    try:
        with st.spinner("로그인 하는 중..."):
            client = OpenAI(api_key=api_key)
            os.environ["OPENAI_API_KEY"] = api_key
        st.success("로그인 성공!")
        st.session_state["logined"] = True
        st.session_state["api_type"] = "open_ai"
        st.session_state["api_base"] = "https://api.openai.com/v1"
        st.session_state["api_version"] = "2023-05-15"

    except:
        st.error("로그인에 실패하였습니다. API Key를 다시 확인해주세요.")
        st.session_state["logined"] = False
