import requests
import streamlit as st

st.set_option("deprecation.showfileUploaderEncoding", False)

st.title("Intelligent document processing with BART")

file = st.file_uploader("Choose a pdf")

#st.button("Purpose of PDF")
#st.button("Summarize pdf")

if st.button('Classify'):
    res = requests.post(url = "http://127.0.0.1:8000/classify", data = file)
    st.subheader(f"This invoice is related to {res}")