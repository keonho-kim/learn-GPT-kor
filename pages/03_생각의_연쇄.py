import os
from openai import OpenAI
import streamlit as st
import time


# Define Functions 
def clear_history():
    st.session_state["messages"] = []

# LOGIN OPTION
if "OPENAI_API_KEY" not in os.environ:
    st.error("🚨 로그인을 먼저 해주세요")
    st.stop()


if "messages" not in st.session_state:
    st.session_state['messages'] = []

st.title("생각의 연쇄 사용하기")

st.sidebar.title("설정")

with st.sidebar:

    history_clear = st.button(label="초기화", on_click=clear_history)
    history_text_space = st.empty()

    if history_clear:
        with history_text_space:
            st.write("대화 기록을 초기화하고 있어요 😉")
            time.sleep(3)
            history_text_space.write("")

    with st.expander("역할 부여하기", expanded=True):
        with st.form("role_form", clear_on_submit=False):
            background_prompt = st.text_area(
                "배경지식/역할",
                height=100,
                key="background_prompt",
                disabled=False,
                label_visibility='hidden'
            )

            background_space = st.empty()

            submit = st.form_submit_button(label="입력")

            if submit:
                background_space.write(
                    "<center>역할이 부여되었어요.</center>",
                    unsafe_allow_html=True
                )
                st.session_state["messages"].append(
                    {"role": "system", "content": background_prompt}
                )
                
        
    with st.expander("생각의 연쇄", expanded=True):
        with st.form("cot_form", clear_on_submit=False):
            cot_prompt = st.text_area(
                "생각의 연쇄",
                height=100,
                key="cot_prompt",
                disabled=False,
                label_visibility='hidden'
            )

            background_space = st.empty()

            submit = st.form_submit_button(label="입력")

            if submit:
                background_space.write(
                    "<center>생각의 연쇄가 입력되었어요..</center>",
                    unsafe_allow_html=True
                )
                st.session_state["messages"].append(
                    {"role": "system", "content": cot_prompt}
                )
        
        
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", 'gpt-4', 'gpt-4-1106-preview']
    model_option = st.selectbox("모델 선택", models)

    with st.expander(label="Max Words"):
        max_tokens = st.slider(
            "Max Words",
            min_value=5,
            max_value= 4000,
            value=2000,
            step=1,
            label_visibility="hidden",
            help="답변의 최대 길이를 설정합니다.",
        )

    with st.expander(label="Temperature"):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.5,
            step=0.1,
            label_visibility="hidden",
            help="답변의 무작위성을 결정합니다. 낮을수록 정형화된 답변을 생성하고, 높을수록 창의적인 답변을 생성합니다.",
        )
    with st.expander(label="Top P"):
        top_p = st.slider(
            "Top P",
            min_value=0.1,
            max_value=1.0,
            step=0.1,
            value=1.0,
            label_visibility="hidden",
            help="단어를 선택 할 때 자유도를 의미합니다. 클수록 다양한 단어를 선택합니다.",
        )
    with st.expander(label="Presence Penalty"):
        presence_penalty = st.slider(
            "Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            label_visibility="hidden",
            help="질문에서 나온 단어들을 기반으로 새로운 단어를 생성 할 지에 영향을 미칩니다. 높을수록 새로운 주제에 대해 이야기합니다.",
        )
    with st.expander(label="Frequency Penalty"):
        frequency_penalty = st.slider(
            "Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            label_visibility="hidden",
            help="질문에서 나온 단어들의 빈도를 기반으로 새로운 단어를 생성 할 지에 영향을 미칩니다. 높을수록 질문 문장에 사용된 단어를 사용합니다.",
        )


cli = OpenAI()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("이야기를 해볼까요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in cli.chat.completions.create(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stream=True,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                ],
            model=model_option,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})