import streamlit as st

st.set_page_config(page_title="GraphRAG Legal | Inicio", page_icon="⚖️", layout="wide")

# Custom CSS for a professional, legal-focused theme and responsiveness
st.markdown("""
<style>
    .main-header {
        font-family: 'Times New Roman', serif;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-family: 'Arial', sans-serif;
        color: #475569;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 40px;
    }
    /* Responsive text sizes */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .sub-header { font-size: 1rem; }
    }
    @media (min-width: 769px) {
        .main-header { font-size: 3rem; }
        .sub-header { font-size: 1.2rem; }
    }
    .faq-title { color: #1E3A8A; font-weight: bold; }
    .footer-text {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>⚖️ Plataforma Legal Inteligente</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Búsqueda y Análisis Jurídico Potenciado por Arquitectura Multi-Agente y GraphRAG</div>", unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### 🔍 ¿Qué es esta herramienta y qué hemos construido?")
    st.write("""
    Esta plataforma es un sistema avanzado de **Inteligencia Artificial Jurídica** que va mucho más allá de un simple chatbot. Hemos diseñado una arquitectura completa (Multi-página) que permite:
    - **Subir y categorizar** documentos legales (Leyes, Códigos de Ética, etc.).
    - **Generar resúmenes automáticos** de los documentos para un vistazo rápido en la sección *Info Actual*.
    - **Visualizar gráficamente** cómo se interconectan los artículos y conceptos jurídicos en un mapa 3D (Sección *Visualizador Grafo*).
    - **Gestionar la base de datos**, con opciones para borrar documentos desactualizados o reiniciar el sistema por completo.
    
    A diferencia de los buscadores tradicionales, nuestra herramienta no solo busca palabras clave, sino que **lee, comprende y extrae las relaciones** entre conceptos legales, creando un Grafo de Conocimiento (Knowledge Graph). Esto permite realizar consultas en lenguaje natural y obtener respuestas fundamentadas, eliminando el riesgo de invenciones (alucinaciones).
    """)
    
    st.markdown("### 🤖 Nuestros Agentes de Inteligencia Artificial")
    st.write("""
    El sistema opera bajo el capó utilizando **dos agentes principales** impulsados por el modelo `gpt-4o-mini` y la tecnología LangGraph, interactuando en tiempo real con la base de datos Neo4j:
    
    1. **Agente Extractor (Data Processor):** Su función es leer los documentos PDF que subes (pedacito por pedacito). Detecta las entidades (Personas, Leyes, Obligaciones) y dibuja las flechas lógicas entre ellas, guardando todo estructurado directamente en Neo4j. También se encarga de redactar los resúmenes ejecutivos.
    2. **Agente Consultor (RAG Agent):** Es el agente con el que platicas en la sección *Agente Legal*. Cuando haces una pregunta, este agente entra a Neo4j, navega por el grafo estructurado, extrae solo la información verídica de la ley, y te redacta una respuesta conversacional precisa.
    
    *(Nota Técnica: Internamente, el Agente Consultor no es una sola pieza, sino que su "cerebro" está dividido en 4 Nodos de LangGraph que trabajan en equipo: un analizador de intención, un buscador local, un buscador global y un redactor final).*
    """)
    
    st.markdown("### 🗣️ ¿Cómo hacer consultas a la IA?")
    st.write("""
    Nuestra plataforma entiende la intención de tu pregunta y utiliza la estrategia correcta para buscar en el grafo de conocimiento:
    
    **1. Búsqueda Local (GraphRAG Puro):** Ideal para explorar conexiones directas o definiciones de la normatividad.
    *   *Ejemplo:* "¿Qué relación hay entre el Código de Ética y la Ley Orgánica de la UJAT?" 
    *   *Ejemplo:* "¿Qué es la ética de la UJAT según los documentos?"
    
    **2. Búsqueda Global (Global Search):** Perfecta para pedir conceptos generales de la institución.
    *   *Ejemplo:* "¿Cuáles son los valores fundamentales que rigen a la institución?"
    
    💡 **Dato Anti-Alucinaciones:** Si haces una pregunta sobre algo que no está en los documentos que subiste (ej. *"¿Cuál es la capital de Francia?"*), el Agente está estrictamente programado para responder que no tiene suficiente información. **Esta es la prueba definitiva de que hemos eliminado las alucinaciones**, garantizando que toda respuesta jurídica sea 100% basada en tus archivos.
    """)
    
    st.info("👈 Usa el menú lateral para acceder al **Agente Legal (Chat)**, **Info Actual** o al **Visualizador de Grafos**.")

with col2:
    st.markdown("### 💡 Preguntas Frecuentes")
    
    with st.expander("¿Si hago clic en refrescar página se va a perder la información procesada?"):
        st.write("NO. Toda la información que se extrae y los fragmentos (chunks) se guardan permanentemente en una base de datos segura en la nube (Neo4j). Si refrescas la página, solo se borrará el historial de tu chat actual, pero el conocimiento extraído permanecerá intacto.")
        
    with st.expander("¿Cuántas personas pueden usarlo de manera paralela?"):
        st.write("La arquitectura del sistema está diseñada para ser altamente escalable. Al usar Neo4j como base de datos y Streamlit como interfaz, cientos o miles de usuarios podrían consultar el sistema en paralelo si la aplicación se despliega en un servidor en la nube con los recursos adecuados.")
        
    with st.expander("¿Puedo abrir varias sesiones en un mismo espacio así como ChatGPT?"):
        st.write("Sí, completamente. Cada vez que abres la plataforma en una nueva pestaña o navegador, Streamlit crea una 'sesión' independiente. Puedes tener múltiples chats paralelos haciendo preguntas distintas sobre la misma base de datos sin que se crucen las respuestas.")
        
    with st.expander("¿Puedo dividir los documentos en bloques (leyes, normas, etc.)?"):
        st.write("¡Sí! Al momento de subir un documento, puedes elegir una **Categoría**. Esta categoría se guarda directamente en el nodo `[Document]` en Neo4j, permitiendo una organización impecable y filtrados a futuro.")

st.divider()

st.markdown("### 📚 Glosario de Conceptos Clave")
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("**GraphRAG:**")
    st.write("Generación Aumentada por Recuperación basada en Grafos. Combina la potencia de la IA con una base de datos estructurada en forma de red, logrando respuestas precisas y evitando alucinaciones.")
    
    st.markdown("**Indexar:**")
    st.write("Proceso de leer, comprender y almacenar el documento en la base de datos de manera organizada para que la inteligencia artificial pueda buscar en él rápidamente.")

with col4:
    st.markdown("**Chunk (Fragmento):**")
    st.write("Pedazo de texto corto en el que se dividen los documentos grandes para que el modelo de IA pueda analizarlos pieza por pieza sin sobrecargar su memoria.")
    
    st.markdown("**Token:**")
    st.write("Unidad básica de medida de texto que procesa la IA. Un token equivale a ~4 caracteres. El costo de la API se mide en cantidad de tokens.")

with col5:
    st.markdown("**Grafo de Conocimiento:**")
    st.write("Mapa mental digital donde la información está conectada lógicamente. Ejemplo: `[Abogado] -> (Defiende a) -> [Cliente]`.")
    
    st.markdown("**PyVis:**")
    st.write("Librería de Python gratuita que permite dibujar e interactuar visualmente con el Grafo de Conocimiento directamente en el navegador.")

st.divider()

st.markdown("### 🚀 Trabajos Futuros y Próximas Funciones (Premium)")
st.info("**Limitación de la Versión Actual:** Por ahora, este agente MVP se basa estrictamente en la información estructurada que extrajo hacia el Grafo de Conocimiento. Esto garantiza alta precisión conceptual, pero limita su capacidad para citar párrafos textuales enormes si no los guardó como relaciones cortas.")
st.success("**Modelo Híbrido (GraphRAG + Vector DB):** En una futura versión Premium, implementaremos un segundo Agente Especializado en Búsqueda Vectorial. Cuando hagas una pregunta, el sistema usará el Grafo para entender el 'mapa conceptual' y usará la Base de Datos Vectorial para extraer la 'cita textual exacta' del PDF original, fusionando ambas en una respuesta hiper-completa e imbatible.")
st.info("**Integración de Voz (Speech-to-Text / Text-to-Speech):** Actualmente la plataforma funciona mediante chat escrito. En fases futuras, se integrarán modelos de IA de audio para permitir a los abogados dictar sus consultas jurídicas por micrófono y escuchar las respuestas narradas por el Agente.")
st.success("**Soporte Nativo a Texto Plano (.txt) para Mayor Certeza:** Aunque nuestro código 'arranca' y convierte PDFs a texto, los PDFs complejos (con tablas, columnas o escaneados) suelen generar un texto sucio que confunde a la IA y deforma el Grafo. En un futuro, permitiremos subir archivos `.txt` previamente limpiados, asegurando que el Grafo de Conocimiento sea infinitamente más perfecto, certero y sin pérdida de información.")

st.markdown(
    """
    <div class='footer-text'>
        <b>Desarrollado por Mtro. Luis Ramón Tercero Martínez González.</b><br>
        <i>Especialista en Agentes y Multi-Agentes basados en IA unimodales y multimodales.</i>
    </div>
    """, 
    unsafe_allow_html=True
)
