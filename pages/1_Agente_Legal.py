import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from src.document_processor import DocumentProcessor
from src.graph_extractor import GraphExtractor
from src.neo4j_manager import Neo4jManager
from src.agent import GraphRAGAgent

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Agente Legal | GraphRAG", page_icon="💬", layout="wide")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "neo4j_manager" not in st.session_state:
    st.session_state.neo4j_manager = Neo4jManager()
if "agent" not in st.session_state:
    st.session_state.agent = GraphRAGAgent(st.session_state.neo4j_manager)

def generate_summary(text):
    """Generates a brief summary from the first 1500 chars of the text."""
    api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    prompt = PromptTemplate.from_template("Redacta un resumen breve (2-3 oraciones) del siguiente texto legal. Texto: {text}")
    response = llm.invoke(prompt.format(text=text[:1500]))
    return response.content

def process_and_index_documents(uploaded_files, category):
    processor = DocumentProcessor()
    extractor = GraphExtractor()
    neo4j = st.session_state.neo4j_manager
    
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)
    
    for i, file in enumerate(uploaded_files):
        st.write(f"Procesando **{file.name}** (Categoría: {category})...")
        chunks, raw_text, page_count = processor.process_uploaded_file(file)
        
        # Generate summary using the first 1500 chars
        summary = "Documento vacío."
        if raw_text:
            summary = generate_summary(raw_text)
        
        # Create Document node with metadata
        # We need a unique doc_id. Let's base it on filename to avoid collisions if we don't clear DB.
        doc_id = f"doc_{file.name.replace(' ', '_')}_{i}"
        chunk_count = len(chunks)
        neo4j.create_document(doc_id, file.name, category=category, summary=summary, page_count=page_count, chunk_count=chunk_count)
        
        for j, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{j}"
            neo4j.create_chunk(chunk_id, doc_id, chunk, j)
            
            graph_data = extractor.extract(chunk)
            
            for entity in graph_data.get("entities", []):
                neo4j.create_entity(entity.get("name"), entity.get("type"), entity.get("description"))
                
            for rel in graph_data.get("relationships", []):
                neo4j.create_relationship(rel.get("source"), rel.get("target"), rel.get("type"), rel.get("description"))
                
        progress_bar.progress((i + 1) / total_files)
        
    st.success("¡Indexación completa! Grafo de Conocimiento generado en Neo4j.")

# --- Sidebar UI ---
with st.sidebar:
    st.title("📄 Configuración y Carga")
    
    openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        
    st.divider()
    
    st.subheader("Subir Documentos")
    doc_category = st.selectbox("Categoría del Documento", ["Leyes", "Normativas", "Código de Ética", "Artículos", "Otro"])
    uploaded_files = st.file_uploader("Cargar documentos legales (PDF, DOCX)", accept_multiple_files=True, type=['pdf', 'docx'])
    
    if st.button("Indexar Documentos"):
        if uploaded_files:
            if not openai_key:
                st.error("Por favor, ingresa tu OpenAI API Key.")
            else:
                with st.spinner("Construyendo el Grafo de Conocimiento... Esto puede tomar un momento."):
                    process_and_index_documents(uploaded_files, doc_category)
        else:
            st.warning("Por favor, sube al menos un documento.")

# --- Main Chat UI ---
st.title("⚖️ Agente Legal GraphRAG")
st.markdown("Haz preguntas sobre los documentos legales indexados. El agente navegará el grafo de conocimiento para darte respuestas precisas sin alucinaciones.")

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Chat input
if user_input := st.chat_input("Escribe tu consulta legal aquí..."):
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Analizando grafo..."):
            response = st.session_state.agent.chat(user_input, st.session_state.chat_history)
            st.markdown(response)
            
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.chat_history.append(AIMessage(content=response))
