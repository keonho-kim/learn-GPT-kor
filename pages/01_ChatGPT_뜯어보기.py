import os
import streamlit as st
from dotenv import load_dotenv
import openai
from openai import OpenAI

load_dotenv()
st.set_page_config(
    page_title="ChatGPT 분해하기",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.header("🧊 ChatGPT의 답변에 영향을 미치는 요소들 ")

st.markdown(
    """
    <br>
    ChatGPT는 단순히 답변을 생성하는 것이 아니라, 다양한 기술적 수치들에 영향을 받습니다.\n
    다양한 수치들을 직접 조절해보면서 심도깊은 이해를 해봅시다.
    <br><br>
    """,
    unsafe_allow_html=True,
)

if "logined" not in st.session_state.keys() or not st.session_state["logined"]:
    st.error("🚨 로그인을 먼저 해주세요")
    st.stop()

if st.session_state["api_type"] == "open_ai":
    models = ["text-davinci-003", "gpt-3.5-turbo"]


with st.empty():
    with st.form(key="my_form"):
        ce, c1, ce, c2, c3 = st.columns([0.1, 3, 0.07, 6, 0.1])
        with c1:
            st.subheader("설정", anchor=None)
            model_option = st.selectbox("모델을 선택해주세요.", models)
            max_tokens = st.slider(
                "Maximum Length",
                min_value=5,
                max_value=4000,
                value=1000,
                step=1,
                label_visibility="visible",
                help="답변의 최대 길이를 설정합니다.",
            )

            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.5,
                step=0.1,
                label_visibility="visible",
                help="답변의 무작위성을 결정합니다. 낮을수록 정형화된 답변을 생성하고, 높을수록 창의적인 답변을 생성합니다.",
            )
            top_p = st.slider(
                "Top P",
                min_value=0.1,
                max_value=1.0,
                step=0.1,
                value=1.0,
                label_visibility="visible",
                help="단어를 선택 할 때 자유도를 의미합니다. 클수록 다양한 단어를 선택합니다.",
            )
            presence_penalty = st.slider(
                "Presence Penalty",
                min_value=-2.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                label_visibility="visible",
                help="질문에서 나온 단어들을 기반으로 새로운 단어를 생성 할 지에 영향을 미칩니다. 높을수록 새로운 주제에 대해 이야기합니다.",
            )
            frequency_penalty = st.slider(
                "Frequency Penalty",
                min_value=-2.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                label_visibility="visible",
                help="질문에서 나온 단어들의 빈도를 기반으로 새로운 단어를 생성 할 지에 영향을 미칩니다. 높을수록 질문 문장에 사용된 단어를 사용합니다.",
            )

        with c2:
            runtime_parameters = {}
            text_prompt = st.text_area(
                label="a",
                disabled=False,
                height=450,
                max_chars=4000,
                label_visibility="hidden",
            )
            running = False
            p0, p1 = st.columns([20, 3])
            with p1:
                submitted = st.form_submit_button("입력", disabled=running)

            if not submitted:
                st.stop()

            running = True
            runtime_parameters["max_tokens"] = max_tokens
            runtime_parameters["temperature"] = temperature
            runtime_parameters["top_p"] = top_p
            runtime_parameters["presence_penalty"] = presence_penalty
            runtime_parameters["frequency_penalty"] = frequency_penalty
            runtime_parameters["stream"] = True

            if st.session_state["api_type"] == "azure":
                runtime_parameters["engine"] = st.session_state["model2deployment"][
                    model_option
                ]
            elif st.session_state["api_type"] == "open_ai":
                runtime_parameters["model"] = model_option

            if model_option in ["text-davinci-003"]:
                runtime_parameters["prompt"] = text_prompt
                res = client.completions.create(**runtime_parameters)
                result = ""
                with st.empty():
                    for x in res:
                        result += x.choices[0].text
                        st.markdown("#### 🤖:\n" + result)
                running = False

            else:
                messages = [
                    {"role": "system", "content": ""},
                    {"role": "user", "content": text_prompt},
                ]
                runtime_parameters["messages"] = messages
                res = client.chat.completions.create(**runtime_parameters)
                result = ""

                with st.empty():
                    for x in res:
                        if x.choices[0].delta.content:
                            result += x.choices[0].delta.content
                            st.markdown("#### 🤖:\n" + result)
                running = False
