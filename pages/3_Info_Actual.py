import streamlit as st
from src.neo4j_manager import Neo4jManager

st.set_page_config(page_title="Info Actual | GraphRAG", page_icon="📑", layout="wide")
st.title("📑 Información Actual (Documentos Indexados)")
st.markdown("Revisa los documentos que actualmente forman parte del Grafo de Conocimiento y lee el resumen generado automáticamente por la IA.")

if "neo4j_manager" not in st.session_state:
    st.session_state.neo4j_manager = Neo4jManager()

def get_documents():
    neo4j = st.session_state.neo4j_manager
    query = """
    MATCH (d:Document)
    RETURN d.id AS id, d.filename AS filename, d.category AS category, 
           d.summary AS summary, d.page_count AS page_count, d.chunk_count AS chunk_count
    """
    try:
        return neo4j.execute_query(query)
    except Exception as e:
        st.error(f"Error consultando la base de datos: {e}")
        return []

docs = get_documents()

if not docs:
    st.info("No hay documentos indexados actualmente en la base de datos Neo4j.")
else:
    st.success(f"Hay {len(docs)} documento(s) indexado(s) en la base de datos.")
    
    for doc in docs:
        filename = doc.get("filename", "Documento Desconocido")
        category = doc.get("category", "General")
        summary = doc.get("summary", "Sin resumen disponible.")
        pages = doc.get("page_count", 0)
        chunks = doc.get("chunk_count", 0)
        
        with st.expander(f"📄 {filename} - [{category}]"):
            st.markdown(f"**Categoría:** {category}")
            st.markdown(f"**Páginas:** {pages}")
            st.markdown(f"**Fragmentos (Chunks) Procesados:** {chunks}")
            st.markdown("### Resumen Ejecutivo")
            st.info(summary)
