import os
import streamlit as st
from pathlib import Path

def save_uploaded_file(uploaded_file):
    """Save uploaded file to data/uploaded_files directory"""
    try:
        # Create directory if it doesn't exist
        upload_dir = Path("data/uploaded_files")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        raise
