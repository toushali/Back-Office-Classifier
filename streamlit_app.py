import json
import tempfile
from pathlib import Path

import streamlit as st

from classifier import process_document

st.set_page_config(page_title="Back Office Document Classifier", layout="centered")

st.title("📄 Back Office Document Classification & Routing Agent")
st.write("Upload an invoice, purchase order, or contract to classify and route it.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    # Save the upload to a temp file since process_document expects a path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Classifying document..."):
        result = process_document(tmp_path)

    st.subheader("Result")

    col1, col2 = st.columns(2)
    col1.metric("Classification", result["label"])
    col2.metric("Confidence", f"{result['confidence']:.0%}")

    st.success(f"Routed to: **{result['routing_department']}**")

    st.write("**Reasoning:**", result["reasoning"])

    st.write("**Key fields extracted:**")
    st.json(result["key_fields"])

    with st.expander("Full raw result"):
        st.json(result)

    Path(tmp_path).unlink(missing_ok=True)  # cleanup temp file