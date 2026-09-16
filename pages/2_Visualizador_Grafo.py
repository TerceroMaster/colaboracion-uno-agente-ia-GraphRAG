import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

from src.neo4j_manager import Neo4jManager

st.set_page_config(page_title="Visualizador de Grafo | GraphRAG", page_icon="🕸️", layout="wide")
st.title("🕸️ Visualizador del Grafo de Conocimiento")
st.markdown("Explora de manera visual cómo están conectados los conceptos, leyes, y entidades en la base de datos Neo4j.")

if "neo4j_manager" not in st.session_state:
    st.session_state.neo4j_manager = Neo4jManager()

# Fetch and display graph statistics
stats = st.session_state.neo4j_manager.get_graph_stats()
col_n, col_r = st.columns(2)
with col_n:
    st.metric(label="🔵 Total de Nodos (Entidades y Documentos)", value=stats.get("node_count", 0))
with col_r:
    st.metric(label="🔗 Total de Relaciones (Aristas)", value=stats.get("rel_count", 0))

st.divider()

def get_graph_data():
    neo4j = st.session_state.neo4j_manager
    # Limit to 300 to prevent browser crash
    query = """
    MATCH (n:Entity)-[r]->(m:Entity)
    RETURN n.name AS source, labels(n)[0] AS source_type,
           type(r) AS rel_type,
           m.name AS target, labels(m)[0] AS target_type
    LIMIT 300
    """
    try:
        results = neo4j.execute_query(query)
        return results
    except Exception as e:
        st.error(f"Error conectando a Neo4j: {e}")
        return []

with st.spinner("Cargando grafo desde Neo4j..."):
    results = get_graph_data()

if not results:
    st.warning("El grafo está vacío o no se pudo conectar. Asegúrate de haber indexado documentos primero en la página del Agente Legal.")
else:
    # Create PyVis network
    net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white", directed=True)
    
    # Configure physics for better layout
    net.force_atlas_2based()
    
    # Add nodes and edges
    added_nodes = set()
    
    # Color mapping for entity types
    color_map = {
        "Document": "#e11d48",
        "Concept": "#2563eb",
        "Organization": "#16a34a",
        "Person": "#d97706",
        "Law": "#9333ea"
    }
    
    for row in results:
        src = row.get("source")
        src_type = row.get("source_type", "Entity")
        tgt = row.get("target")
        tgt_type = row.get("target_type", "Entity")
        rel = row.get("rel_type")
        
        if src not in added_nodes:
            net.add_node(src, label=src, title=src_type, color=color_map.get(src_type, "#64748b"))
            added_nodes.add(src)
            
        if tgt not in added_nodes:
            net.add_node(tgt, label=tgt, title=tgt_type, color=color_map.get(tgt_type, "#64748b"))
            added_nodes.add(tgt)
            
        net.add_edge(src, tgt, title=rel, label=rel)
    
    # Save and read graph as HTML
    try:
        path = "html_files"
        if not os.path.exists(path):
            os.makedirs(path)
        net.save_graph(f"{path}/graph.html")
        HtmlFile = open(f"{path}/graph.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height=650)
    except Exception as e:
        st.error(f"Error renderizando el grafo: {e}")
        
    st.info("💡 **Tip:** Puedes hacer zoom, arrastrar los nodos y pasar el ratón por encima de ellos o las flechas para ver más información.")
