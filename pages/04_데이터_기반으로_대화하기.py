import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message
import time
from utils import util
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
load_dotenv()


def clear_history():
    st.session_state.past = []
    st.session_state.generated = []
    st.session_state.data_loaded = False
    st.session_state.data = pd.DataFrame()
    st.session_state.file = ""


st.set_page_config(
    page_title="데이터 기반으로 대화하기",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)


if "logined" not in st.session_state.keys() or not st.session_state["logined"]:
    st.error("🚨 로그인을 먼저 해주세요")
    st.stop()


if "file" not in st.session_state:
    st.session_state.file = ""

if "past" not in st.session_state:
    st.session_state.past = []
if "generated" not in st.session_state:
    st.session_state.generated = []

if "data" not in st.session_state:
    st.session_state.data = None

models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", 'gpt-4', 'gpt-4-32k']

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
    st.title("🧾 데이터 기반으로 대화하기")
    st.write(
        """
        <br>
        언어 모델이 다양한 일을 할 수 있지만, 단순히 대화만 한다면 언어 모델의 진면목을 이끌어내지 못한 것입니다.
        <br>
        본질적으로 인공지능 모델은 새로운 데이터를 입력 받아 데이터에 기반해서 답변 해줄 수 있습니다.
        <br>
        물론, OpenAI 기본 대화 기능으로는 불가능하지만, 어떤 느낌인지 체험해보는 것만으로 가치가 있겠죠?
        <br>
        데이터를 기반으로 대화해봅시다!        
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
            value=0.0,
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


de0, d1, de1 = st.columns([0.07, 5, 0.07])

with d1:
    show_data = False
    data_session = st.form("Read Data", clear_on_submit=False)
    with data_session:
        st.write(
            """
            <font size=3>데이터 불러오기</font>
            """,
            unsafe_allow_html=True,
        )
        data_c0, data_center_margin, data_c1, data_right_margin = st.columns(
            [25, 0.5, 2, 0.15]
        )
        with data_c0:
            st.session_state.file = st.file_uploader(
                ".CSV 또는 엑셀 파일을 입력해주세요.",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
            )

        with data_c1:
            st.write("<br>", unsafe_allow_html=True)
            submit_data = st.form_submit_button(label="입력", use_container_width=True)

    if submit_data:
        try:
            success = st.success("데이터를 불러오고 있습니다.")
            time.sleep(1.5)
            success.empty()
            st.session_state.data = util.read_data(st.session_state.file)
            d1.dataframe(st.session_state.data, use_container_width=True)

        except:
            error = st.error("데이터를 확인해주세요.")
            time.sleep(0.5)
            error.empty()


question_form = st.form("question_form", clear_on_submit=True)
with question_form:
    st.write("질문을 입력해주세요.")
    ql, q1, qc, q2, qr = st.columns([0.3, 30, 0.5, 3, 0.7])
    with q1:
        user_input = st.text_area(
            "질문을 입력해주세요.", "", key="input", label_visibility="collapsed", height=150
        )
    with q2:
        submit = st.form_submit_button(label="입력")


messages = []
if submit:
    loading_text_space = st.empty()
    loading_text_space.write(
        "<center>답변을 생성하고 있습니다...⏰</center>", unsafe_allow_html=True
    )

    llm = OpenAIChat(
        openai_api_key=st.session_state.api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        model=model_option,
    )

    if st.session_state.data is not None:
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=st.session_state.data,
            max_iterations=10,
            verbose=True,
            return_intermediate_steps=True,
            memory=ConversationBufferMemory(memory_key="chat_history"),
            handle_parsing_errors="질문을 더  상세히 입력해주세요 😅",
        )

        full_res = agent({"input": user_input})
        res = full_res["output"]
        procedure_log = ""

        for steps in full_res["intermediate_steps"]:
            procedure_log += "-" * 5 + "\n" + steps[0][2] + "\n"
            procedure_log = procedure_log.replace("python_repl_ast", "Python")

        for i in range(len(st.session_state["generated"])):
            messages.append({"role": "user", "content": st.session_state["past"][i]})
            messages.append(
                {
                    "role": "assistant",
                    "content": st.session_state["generated"][i],
                }
            )

        messages.append({"role": "user", "content": user_input})

        st.session_state.past.append(user_input)
        st.session_state.generated.append(
            f"{'='*5}\nAI의 생각\n{'='*5}\n\n"
            + procedure_log
            + f"{'-'*5}\n\n"
            + f"{'='*5}\n결과\n{'='*5}\n\n"
            + res
        )

        c_l, c_body, c_r = st.columns([2, 25, 2])
        with c_body:
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

            d1.dataframe(st.session_state.data, use_container_width=True)
            loading_text_space.write("")
