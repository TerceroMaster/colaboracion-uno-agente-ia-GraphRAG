# Plataforma Legal Inteligente - GraphRAG

Esta plataforma es un sistema avanzado de **Inteligencia Artificial Jurídica** diseñado para analizar documentos legales complejos utilizando la arquitectura **GraphRAG** (Generación Aumentada por Recuperación basada en Grafos).

## 🚀 Características Principales

1. **Agente Legal (Chat):** Permite subir documentos legales (PDF, DOCX) e interactuar con ellos mediante preguntas en lenguaje natural. Utiliza LangGraph y OpenAI (`gpt-4o-mini`) para extraer entidades y relaciones, guardándolas estructuradas en Neo4j.
2. **Visualizador de Grafos:** Un mapa 3D interactivo (PyVis) donde puedes explorar visualmente cómo se conectan los conceptos jurídicos.
3. **Info Actual:** Panel de control para revisar rápidamente los documentos indexados, su categoría, cantidad de páginas, fragmentos, y un **resumen automático** generado por la IA.
4. **Gestión de Datos:** Herramienta para eliminar documentos específicos o formatear la base de datos por completo.

> **Limitación Actual:** En esta versión inicial (MVP), el agente extrae únicamente el "mapa conceptual" (entidades y relaciones) hacia Neo4j. Se limita a responder basado estrictamente en las conexiones que identificó, sin acceder al texto masivo crudo al momento de responder.
>
> **Trabajo Futuro (Modelo Híbrido Premium):** Para solucionar lo anterior, se desarrollará un segundo Agente Especializado (VectorRAG) que buscará en paralelo en una base de datos vectorial para recuperar y citar párrafos exactos y extensos, complementando las respuestas lógicas del Grafo de Conocimiento.
> 
> **Trabajo Futuro (Soporte Nativo a Texto Plano):** Para entornos de producción, se permitirá subir archivos de texto plano purificados (`.txt`). Aunque el sistema convierte PDFs a texto internamente, los PDFs complejos (tablas, columnas) generan extracciones "sucias" que confunden a la IA y deforman el Grafo. Permitir la subida de texto puro garantizará un Grafo de Conocimiento infinitamente más perfecto, certero y sin pérdida de información.

## 🛠️ Tecnologías Utilizadas
- **Frontend:** Streamlit
- **Base de Datos de Grafos:** Neo4j (AuraDB)
- **Modelos LLM:** OpenAI (GPT-4o-mini)
- **Framework de Orquestación:** LangChain & LangGraph
- **Procesamiento de Documentos:** PyPDF2, python-docx

## ☁️ Despliegue en Streamlit Community Cloud

Si vas a desplegar esta aplicación en Streamlit Cloud (`share.streamlit.io`), es **obligatorio** configurar las variables de entorno (Secrets) para que la aplicación no falle al iniciar.

### Instrucciones de Despliegue:

1. Asegúrate de que este repositorio esté en GitHub (rama `master` o `main`).
2. Ve a [share.streamlit.io](https://share.streamlit.io/) y haz clic en **Create App**.
3. Selecciona tu repositorio, tu rama y el archivo principal: `app.py`.
4. **Antes de presionar "Deploy"**, haz clic en **Advanced settings...**.
5. En la sección **Secrets**, copia y pega tus credenciales exactas (sustituye los valores por los tuyos reales):

```toml
OPENAI_API_KEY="sk-tu-clave-de-openai"
NEO4J_URI="neo4j+s://xxxxxx.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="tu-password-de-neo4j-aura"
```

6. Haz clic en **Save** y luego en **Deploy**.

> **Nota:** Si olvidas agregar los secrets, la aplicación mostrará errores de conexión a `localhost:7687` o errores de OpenAI (`Missing credentials`). Si eso pasa, simplemente ve a "Manage App" (abajo a la derecha), entra a la configuración (tres puntos) -> Settings -> Secrets, pon tus claves, guarda, y reinicia la app.

## 💻 Ejecución Local

Para correr el proyecto en tu propia máquina:

1. Clona el repositorio.
2. Crea un entorno virtual y actívalo.
3. Instala las dependencias: `pip install -r requirements.txt`
4. Crea un archivo `.env` en la raíz del proyecto con las mismas variables descritas en la sección anterior.
5. Ejecuta la aplicación: `streamlit run app.py`

---
*Desarrollado por Mtro. Luis Ramón Tercero Martínez González.*
*Especialista en Agentes y Multi-Agentes basados en IA unimodales y multimodales.*
