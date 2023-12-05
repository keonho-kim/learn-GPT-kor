import time
import re
import os
from utils import util
import pandas as pd
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

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

# LOGIN OPTION
if "OPENAI_API_KEY" not in os.environ:
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

models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", 'gpt-4', 'gpt-4-1106-preview']


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🧾 데이터 기반으로 대화하기")

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
    model_option = st.selectbox("모델 선택", 
                                options=models,
                                index=models.index('gpt-4'))

    with st.expander(label="Max Words"):
        max_tokens = st.slider(
        "Max Words",
        min_value=5,
        max_value=30000 if ('32k' in model_option) else 12000 if ('16k' in model_option) else 4000,
        value=2500,
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
        
        st.session_state.file = st.file_uploader(
            ".CSV 또는 엑셀 파일을 입력해주세요.",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )

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
    user_input = st.text_area(
        "질문을 입력해주세요.", "", key="input", label_visibility="collapsed", height=150
        )
    submit = st.form_submit_button(label="입력")


system_instruction = """
        너는 지금부터 주어진 데이터를 분석하는 역할을 하게 될거야. 
        너는 한국에서 일하고 있어. 항상 한국어로 답을 해야하.
        고객들에게 아주 중요한 일이라서, 잘하는만큼 더 많은 팁을 받게 될거야. 
        """

messages = [
    {
        "role": "system", 
        "content": system_instruction
        }
    ]

if submit:
    
    messages.append({"role": "user", "content": user_input})
    
    loading_text_space = st.empty()
    loading_text_space.write(
        "<center>답변을 생성하고 있습니다...⏰</center>", unsafe_allow_html=True
    )
    
    llm = ChatOpenAI(
        openai_api_key=os.environ["OPENAI_API_KEY"],
        model=model_option,
        streaming=True,
        temperature=temperature,
        max_tokens=max_tokens,
        model_kwargs={
            'top_p' : top_p,
            'frequency_penalty' : frequency_penalty,
            'presence_penalty' : presence_penalty
            }
    )

    
    if st.session_state.data is not None:
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=st.session_state.data,
            max_iterations=5,
            verbose=True,
            return_intermediate_steps=True,
            memory=ConversationBufferMemory(memory_key="chat_history"),
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True
        )

        full_res = agent(
            {
                "input": user_input,
                "context" : system_instruction
             },
            )
        
        res = full_res["output"]
        log = ""
        
        pattern_brace = r"\{([^}]*)\}"
        for idx, steps in enumerate(full_res["intermediate_steps"]):
            if len(full_res["intermediate_steps"]) > 0:
                if len(full_res["intermediate_steps"]) > 1:
                    log += f"Step {idx+1}:\n"
                q = re.findall(pattern_brace, [__ for __ in steps[0]][2][1])[0]
                q = q.split(': ')[-1]
                first_str = q[0]
                q = q.replace(first_str, '')
                log += q
                log += '\n\n\n'
            else:
                log += '코드 실행 기록 없음.\n\n'    
            
        
        for i in range(len(st.session_state["generated"])):
            messages.append({"role": "user", "content": st.session_state["past"][i]})
            messages.append(
                {
                    "role": "assistant",
                    "content": st.session_state["generated"][i],
                }
            )

        

        st.session_state.past.append(user_input)
        st.session_state.generated.append(
            "작업 기록\n\n\n"
            + f"{log}"
            + f"\n\n답변\n\n\n"
            + f"{res}"
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
