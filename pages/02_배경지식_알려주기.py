import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from dotenv import load_dotenv
import time

load_dotenv()


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
    page_title="역할/배경지식을 주고 대화해보기",
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
    st.title("📝 ChatGPT에 역할/배경지식을 알려주기 ")
    st.markdown(
        """
        <br>
        컴퓨터에게 원하는 답변을 하도록 길들이는 방법 중 가장 유명한 것은 <b>배경지식 부여하기</b> 입니다.
        <br>
        흔히 <b>역할 부여 (Role-Playing)</b>라고 불리는 이 방식은 언어 모델이 <b>대화의 맥락</b>을 생성하게 합니다.
        <br>
        맥락을 파악한다는게 무슨 의미일까요? 사람이 대화하는 방식을 생각해보겠습니다.
        <br>
        적절한 대답을 하기 위해서 대화가 어느정도 진전 될 필요가 있지요?
        <br>
        그 때, 사람은 대화의 맥락을 파악하는 것을 통해서 '지금 가장 적절한 이야기'를 하는 것 입니다.
        <br>
        인공지능도 똑같습니다! 사람처럼 '지금 가장 적절한 대답'을 하기 위해서 맥락을 파악 할 필요가 있는 것 입니다.
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


ce, c1, ce, c2, c3 = st.columns([0.07, 3, 0.07, 6, 0.07])


with c1:
    with st.form("instruction_form", clear_on_submit=False):
        background_prompt = st.text_area(
            "배경지식/역할 부여하기",
            height=250,
            key="background_prompt",
            disabled=False,
        )

        background_space = st.empty()
        b_0, b_1, b_2 = st.columns([10, 5, 4])

        with b_1:
            background_clear = st.form_submit_button(label="초기화")

        if background_clear:
            background_space.write(
                "<center> 초기화 되었습니다 🤖 </center>", 
                unsafe_allow_html=True
            )
            st.session_state["messages"] = []

        with b_2:
            submit = st.form_submit_button(label="입력")

        if submit:
            background_space.write(
                "<center>정보가 입력되었습니다 🤖</center>",
                unsafe_allow_html=True
            )
            st.session_state["messages"].append(
                {"role": "system", "content": background_prompt}
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
        cli=OpenAI(api_key=st.session_state['api_key'])
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
