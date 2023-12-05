# Learn GPT 

> <B>Declaimer</B>
> 본 프로젝트는 MIT License로, 무상으로 사용 가능합니다. 다만, <B>Issue에 사용한다는 글</B>을 남겨주시면 감사하겠습니다. 
> (확인 즉시 Closed로 전환하도록 하겠습니다!)
    

## Welcome !

&nbsp;&nbsp;&nbsp;&nbsp;본 프로젝트는 ML/DL 분야에 지식이 없으신 분들께서 OpenAI Playground 기능을 국문으로 사용 하실 수 있도록 작성되었습니다.
최소한의 기능들만 구현하였으며, 약 1~2시간을 소요하여 ChatGPT / GPT-4를 체험하실 수 있도록 구성하였습니다.

&nbsp;&nbsp;&nbsp;&nbsp; API Key는 GPT-4가 지원하도록 $5 이상 유료로 결제된 계정을 권장드립니다. 
(실제 사용에는 큰 지장이 없으나, GPT-4-preview까지 체험을 염두에 두고 작성하였습니다.)

## Functions

```
- 개인 API Key를 통한 로그인 기능
- GPT-3.5-turbo (이하 ChatGPT)의 Parameters에 대한 설명과 GPT-3와의 성능 비교 체험
- 역할 부여 (Role-Playing) 
    - ChatGPT와 GPT-4 지원 (Single Instruction)
- 역할 부여와 생각의 연쇄 (Chain-of-Thought; CoT) 
    - ChatGPT와 GPT-4 지원 (Double Instruction)
- CSV 파일을 업로드하여 ChatGPT/GPT-4와의 대화를 통한 데이터 분석하기 : 
    - ChatGPT, GPT-4 지원 LangChain
```

## Installation

- 프로젝트 수행 환경 : Silicon Mac (M1~)

- 다음의 코드를 터미널에서 한 줄 씩 실행하시면 됩니다. 
```
git clone https://github.com/keonho-kim/learn-GPT-kor.git
cd learn-GPT_kor && pip install -r requirements.txt
streamlit run Hello.py
```
