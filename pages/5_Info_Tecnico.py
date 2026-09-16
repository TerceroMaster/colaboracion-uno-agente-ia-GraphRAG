import streamlit as st

st.set_page_config(page_title="Info Técnico | GraphRAG", page_icon="⚙️", layout="wide")

st.title("⚙️ Información Técnica e Ingeniería del Sistema")
st.markdown("Esta sección detalla la arquitectura de backend, el modelo de agentes y el código principal (LangGraph) que impulsa la **Plataforma Legal Inteligente**.")

st.header("1. Stack Tecnológico y Librerías Core")
st.markdown("""
El proyecto está construido sobre un ecosistema de Python moderno, utilizando las siguientes librerías principales:
- **`langchain` & `langgraph`**: Frameworks de orquestación. LangGraph se usa para crear flujos de trabajo cíclicos y con estado (StateGraph) que simulan el razonamiento de un agente.
- **`langchain-openai`**: Para la integración con los modelos de lenguaje (LLM), específicamente `gpt-4o-mini`.
- **`neo4j`**: Driver oficial para conectar con la base de datos de grafos AuraDB.
- **`pyvis`**: Librería para la renderización de grafos de red interactivos (física de nodos) en el visualizador.
- **`streamlit`**: Framework de frontend para crear la interfaz web interactiva.
- **`PyPDF2` & `python-docx`**: Para la extracción de texto crudo de los documentos subidos.
""")

st.header("2. ¿Cómo funciona la Indexación y Relación de Documentos?")
st.info("""
**La Magia detrás del Grafo:**
Cuando subes un documento legal, no se guarda como texto plano. Ocurre este proceso:
1. **Chunking**: El documento se divide en pequeños fragmentos (chunks) de ~600 caracteres.
2. **Extracción (LLM)**: Cada fragmento pasa por `gpt-4o-mini` con un *prompt* que le ordena: *"Extrae Entidades (Leyes, Conceptos, Personas) y las Relaciones entre ellas"*.
3. **Fusión en el Grafo (Merge)**: Neo4j toma estas entidades. Si en la página 1 habla del *Rector* y en la página 50 vuelve a hablar del *Rector*, **Neo4j no crea dos nodos**. Fusiona ambos en un solo nodo central `(Person: Rector)`. 
4. **Relaciones Inter-Documento**: Si subes el *Código de Ética* y luego la *Ley Orgánica*, y ambos mencionan al *Rector*, el nodo del Rector servirá como "puente" conectando las reglas de ambos documentos. ¡Así es como los documentos se relacionan automáticamente!
""")

st.header("3. Arquitectura del Agente (LangGraph)")
st.markdown("""El Agente de Consultas funciona como una máquina de estados finitos (`StateGraph`). Su flujo de trabajo se define en `src/agent.py`. 

A nivel conceptual, el usuario interactúa con un solo **"Agente Consultor"**, pero internamente, el "cerebro" de este agente está dividido en **4 Nodos** (sub-funciones especializadas) que trabajan en equipo. 
Además, el agente utiliza un **`AgentState`** como una **Memoria a Corto Plazo** (una libreta de apuntes temporal que se borra al reiniciar la app) para pasarse información entre sus nodos durante los segundos que tarda en responder, mientras que Neo4j actúa como su **Memoria a Largo Plazo** (permanente).""")

st.code("""
# Pseudocódigo de la topología del Agente (LangGraph)
from langgraph.graph import StateGraph, END

# 1. Definimos el estado del Agente (memoria a corto plazo)
class AgentState(TypedDict):
    messages: list
    context: str
    strategy: str

# 2. Inicializamos el Grafo
workflow = StateGraph(AgentState)

# 3. Añadimos los "Nodos" (las funciones o cerebros del agente)
workflow.add_node("analyzer", agent.analyze_query)      # Decide qué tipo de búsqueda hacer
workflow.add_node("local_search", agent.local_search)   # Busca entidades específicas
workflow.add_node("global_search", agent.global_search) # Busca conceptos panorámicos
workflow.add_node("generator", agent.generate_response) # Redacta la respuesta final

# 4. Definimos cómo fluye la información (Edges)
workflow.set_entry_point("analyzer")

# 5. Enrutamiento dinámico basado en la decisión del analyzer
workflow.add_conditional_edges(
    "analyzer",
    lambda state: state['strategy'],
    {
        "local": "local_search",
        "global": "global_search",
        "direct": "generator"
    }
)

# 6. Todos los caminos llevan al generador para hablar con el usuario
workflow.add_edge("local_search", "generator")
workflow.add_edge("global_search", "generator")
workflow.add_edge("generator", END)

# Compilamos el agente
app = workflow.compile()
""", language="python")

st.header("4. Clases y Backend Principal")
st.markdown("""
El backend está dividido en 3 pilares de Programación Orientada a Objetos:
1. **`Neo4jManager` (`src/neo4j_manager.py`)**: Clase Singleton (o casi) encargada de mantener la conexión persistente por sesión a AuraDB. Contiene los métodos `execute_query` y la inyección de Cypher.
2. **`DocumentProcessor` y `GraphExtractor` (`src/graph_extractor.py`)**: Se encargan del pipeline de indexación. Aquí se definen los *prompts* de extracción y se mapean las salidas JSON del LLM hacia sentencias `MERGE` de Cypher para Neo4j.
3. **`LegalAgent` (`src/agent.py`)**: Encapsula el motor de LangGraph, la lógica de *fallback* (si falla la búsqueda local, intentar global), y maneja el historial conversacional.
""")

st.success("Toda esta arquitectura permite que el sistema responda preguntas jurídicas con una precisión determinista, eliminando las alucinaciones típicas de los chatbots convencionales.")
