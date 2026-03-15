import streamlit as st
import requests
import json
from pathlib import Path
import sys
import os
import re
import time

sys.path.insert(0, str(Path.cwd()))

from rag.chain import RAGChain
from rag.core.indexing.indexer import DocumentIndexer
from app.config import settings

st.set_page_config(
    page_title="Spacer Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding: 1rem 2rem;
    }
    .stChatMessage {
        border-radius: 0.5rem;
    }
    div[data-testid="stButton"] button {
        border-radius: 20px;
        border: 1px solid #4B4B4B;
        padding: 0.2rem 1rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = RAGChain() 

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = str(time.time())

if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = None

def handle_suggestion_click(suggestion_text):
    st.session_state.suggestion_clicked = suggestion_text

with st.sidebar:
    st.title("Upload Materi")
    
    uploaded_file = st.file_uploader(
        "Pilih dokumen untuk ditambahkan ke knowledge base", 
        type=["pdf", "txt", "csv", "docx"],
        key=st.session_state.uploader_key
    )
    
    if uploaded_file is not None:
        if st.button("Proses Dokumen", use_container_width=True):
            with st.spinner("Memproses dan Menganalisis Dokumen..."):
                save_path = Path(uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    indexer = DocumentIndexer()
                    indexer.ingest_file(str(save_path))
                    st.success(f"'{uploaded_file.name}' berhasil ditambahkan ke knowledge base!")
                    
                    st.session_state.uploader_key = str(time.time())
                    
                    time.sleep(1) 
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Gagal memproses dokumen: {e}")
                finally:
                    if save_path.exists():
                        os.remove(save_path)

st.title("Spacer Chat")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Halo! Saya adalah asisten AI dari Spacer Chat. Ada materi perkuliahan yang ingin kamu tanyakan hari ini?")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant" and "suggestions" in message and i == len(st.session_state.messages) - 1:
            if message["suggestions"]:
                st.markdown("**Pertanyaan Terkait:**")
                for q in message["suggestions"][:3]:
                    st.button(q, key=f"sugg_{i}_{q}", on_click=handle_suggestion_click, args=(q,))

prompt = st.chat_input("Tanyakan sesuatu...")

if st.session_state.suggestion_clicked and not prompt:
    prompt = st.session_state.suggestion_clicked
    st.session_state.suggestion_clicked = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban..."):
            try:
                result = st.session_state.rag_chain.run(prompt)
                
                raw_content = result.get('content', 'Maaf, saya tidak menemukan jawaban yang relevan di materi perkuliahan.')
                suggested_questions = result.get('suggested_questions', [])
                
                main_content = raw_content
                extracted_suggestions = []
                
                split_keywords = ["Pertanyaan Reflektif:", "Pertanyaan Terkait:", "Pertanyaan Terkait", "Pertanyaan Reflektif"]
                
                for kw in split_keywords:
                    if kw in raw_content:
                        parts = raw_content.split(kw)
                        main_content = parts[0].strip()
                        suggestions_text = parts[1].strip()
                        
                        lines = suggestions_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('- ') or line.startswith('* '):
                                extracted_suggestions.append(line[2:].strip())
                            elif re.match(r'^\d+\.\s', line):
                                extracted_suggestions.append(re.sub(r'^\d+\.\s', '', line).strip())
                        break
                
                if extracted_suggestions and not suggested_questions:
                    suggested_questions = extracted_suggestions

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": main_content,
                    "suggestions": suggested_questions
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")