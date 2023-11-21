from typing import TextIO
import streamlit as st
import pandas as pd
from langchain.llms import OpenAI
from langchain.agents import create_pandas_dataframe_agent


def read_data(file: st.file_uploader) -> pd.DataFrame:
    """Read Dataset from the uploaded file

    Args:
        file : st.file_uploader instance

    Returns:
        pd.DataFrame: Pandas DataFrame for input.
    """

    if file.name.split(".")[-1].lower() in ["csv"]:
        df = pd.read_csv(file)
    elif file.name.split(".")[-1].lower() in ["xlsx", "xls"]:
        df = pd.read_excel(file, sheet_name=0, header=0, skiprows=[0])

    return df
