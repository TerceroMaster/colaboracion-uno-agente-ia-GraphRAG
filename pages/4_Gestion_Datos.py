import streamlit as st
from src.neo4j_manager import Neo4jManager

st.set_page_config(page_title="Gestión de Datos | GraphRAG", page_icon="⚙️", layout="wide")
st.title("⚙️ Gestión de Base de Datos (Reset)")
st.markdown("Administra los documentos alojados en la base de datos Neo4j. Puedes borrar documentos individuales que estén desactualizados o resetear toda la base de datos.")

if "neo4j_manager" not in st.session_state:
    st.session_state.neo4j_manager = Neo4jManager()

def get_documents():
    neo4j = st.session_state.neo4j_manager
    query = """
    MATCH (d:Document)
    RETURN d.id AS id, d.filename AS filename, d.category AS category
    """
    try:
        return neo4j.execute_query(query)
    except Exception as e:
        st.error(f"Error consultando la base de datos: {e}")
        return []

st.markdown("### Documentos Indexados")
docs = get_documents()

if not docs:
    st.info("No hay documentos para gestionar.")
else:
    for doc in docs:
        doc_id = doc.get("id")
        filename = doc.get("filename")
        category = doc.get("category")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"📄 **{filename}** *(Categoría: {category})*")
        with col2:
            if st.button("🗑️ Borrar", key=f"del_{doc_id}"):
                with st.spinner("Borrando documento y sus fragmentos..."):
                    st.session_state.neo4j_manager.delete_document(doc_id)
                st.success("Documento borrado exitosamente.")
                st.rerun()

st.divider()
st.markdown("### ⚠️ Peligro: Formateo Total")
st.warning("Esta acción borrará absolutamente todos los nodos, entidades, relaciones y documentos de Neo4j. Usa esto solo si quieres reiniciar el sistema desde cero para hacer nuevas pruebas.")

if st.button("🚨 BORRAR TODA LA BASE DE DATOS", type="primary"):
    with st.spinner("Formateando Neo4j..."):
        st.session_state.neo4j_manager.clear_database()
    st.success("Base de datos formateada exitosamente.")
    st.rerun()
