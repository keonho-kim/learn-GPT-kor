import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()


def clear_history():
    st.session_state["past"] = []
    st.session_state["generated"] = []


if "mesasges" not in st.session_state:
    st.session_state["messages"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "logined" not in st.session_state.keys() or not st.session_state["logined"]:
    st.error("🚨 로그인을 먼저 해주세요")
    st.stop()

if st.session_state["api_type"] == "open_ai":
    models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613"]

st.set_page_config(
    page_title="Chain-of-Thought",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

explanation_0, explanation_1, explanation_2 = st.columns([0.07, 10, 0.07])
with explanation_1:
    st.title("⛓️ ChatGPT와 생각의 연쇄(Chain-of-Thought)")
    st.write(
        """
        <br>
        최신 기법 중 하나인 생각의 연쇄 (Chain-of-Thought)는 컴퓨터가 <b>차근차근</b> 생각하도록 하는 것 입니다.
        <br>
        생각의 연쇄는 <a href="https://arxiv.org/pdf/2205.11916.pdf" target="_blank">2022년에 도쿄대/구글 공동 연구진이 제안한 방법</a>입니다.
        <br>
        이 기법은 수학과 같이 차근차근 생각하는 것이 필요한 영역에서 성능을 대폭 향상 시키는 효과를 보였습니다.
        <br>
        사람의 생각 방식과 유사하게, 단계적으로 '추론(Reasoning)'의 과정을 거치도록 함으로써, 큰 문제를 세부적으로 나누어 답변을 하게하는 효과가 있습니다.
        <br>
        아직 연구가 꾸준히 진행 중인 <b>미지의 분야</b>입니다! 여러분들만의 <b>마법의 문장</b>을 만들어보세요!
        <br><br>
        """,
        unsafe_allow_html=True,
    )


st.sidebar.title("설정")

with st.sidebar:
    history_clear = st.button(label="초기화", on_click=clear_history)
    history_text_space = st.empty()

    if history_clear:
        with history_text_space:
            st.write("대화 기록을 초기화하고 있어요 😉")
            time.sleep(3)
            history_text_space.write("")

    st.write(
        """
        <font size=2>모델 설정</font>
        """,
        unsafe_allow_html=True,
    )
    model_option = st.selectbox("Select Model", models)
    with st.expander(label="Max Words"):
        if model_option in ["gpt-3.5-turbo-0613"]:
            max_tokens = st.slider(
                "Max Words",
                min_value=5,
                max_value=4000,
                value=1000,
                step=1,
                label_visibility="hidden",
                help="답변의 최대 길이를 설정합니다.",
            )
        else:
            max_tokens = st.slider(
                "Max Words",
                min_value=5,
                max_value=16000,
                value=1000,
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


submit_background, submit_cot = False, False
background_prompt, cot_prompt = "", ""

ce, c1, ce, c2, c3 = st.columns([0.07, 3, 0.07, 6, 0.07])

with c1:
    with st.form("instruction_form1", clear_on_submit=False):
        background_prompt = st.text_area(
            "배경지식/역할 부여하기",
            disabled=False,
            height=250,
            key="background_prompt",
        )

        background_space = st.empty()

        b_0, b_1, b_2 = st.columns([10, 5, 4])

        with b_1:
            background_clear = st.form_submit_button(label="초기화")
        if background_clear:
            background_space.write(
                "<center> 초기화 되었습니다 🤖 </center>", unsafe_allow_html=Tru
            e)
            if submit_cot and cot_prompt:
                st.session_state["messages"] = [
                    {"role": "system", "content": cot_prompt}
                ]
            else:
                st.session_state["messages"] = []

        with b_2:
            submit_background = st.form_submit_button(label="입력")
        if submit_background:
            background_space.write(
                "<center>정보가 입력되었습니다 🤖</center>", unsafe_allow_html=Tru
            e)
            st.session_state["messages"].append(
                {"role": "system", "content": background_prompt}
            )

    with st.form("instruction_form2", clear_on_submit=False):
        cot_prompt = st.text_area(
            "생각의 연쇄 입력하기",
            disabled=False,
            height=200,
            key="cot_prompt",
        )

        cot_space = st.empty()

        cot_0, cot_1, cot_2 = st.columns([10, 5, 4])

        with cot_1:
            cot_clear = st.form_submit_button(label="초기화")
        if cot_clear:
            cot_space.write("<center> 초기화 되었습니다 🤖 </center>", unsafe_allow_html=True)
            if submit_background and background_prompt:
                mesages = [{"role": "system", "content": background_prompt}]
            else:
                st.session_state["messages"] = []

        with cot_2:
            submit_cot = st.form_submit_button(label="입력")
        if submit_cot:
            cot_space.write("<center>정보가 입력되었습니다 🤖</center>", unsafe_allow_html=True)
            st.session_state["messages"].append(
                {"role": "system", "content": cot_prompt}
            )


with c2:
    running = False
    with st.form("submit_form", clear_on_submit=True):
        user_input = st.text_area("질문을 입력해주세요.", "", key="input", disabled=running)
        p0, p1 = st.columns([20, 3])
        with p1:
            submit = st.form_submit_button(label="입력")

    loading_text_space = st.empty()

    if submit:
        with loading_text_space:
            st.write("<center>답변을 생성하고 있습니다...⏰</center>", unsafe_allow_html=True)

        for i in range(len(st.session_state["generated"])):
            st.session_state["messages"].append(
                {"role": "user", "content": st.session_state["past"][i]}
            )
            st.session_state["messages"].append(
                {"role": "assistant", "content": st.session_state["generated"][i]}
            )

        st.session_state["messages"].append({"role": "user", "content": user_input})

        running = True

        if st.session_state["api_type"] == "open_ai":
            res = client.chat.completions.create(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stream=True,
                messages=st.session_state["messages"],
                model=model_option,
            )

        result = ""

        with st.empty():
            for x in res:
                if "content" in x.choices[0].delta.keys():
                    result += x.choices[0].delta.content

        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(result)

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(
                st.session_state["past"][i],
                avatar_style="fun-emoji",
                is_user=True,
                key=str(i) + "_user",
            )
            message(
                st.session_state["generated"][i],
                avatar_style="thumbs",
                is_user=False,
                key=str(i),
                seed=123,
            )

        loading_text_space.write("")
