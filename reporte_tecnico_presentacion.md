# Plataforma Legal Inteligente basada en GraphRAG y Agentes IA
**Reporte Técnico de Arquitectura y Resultados**

---

## 1. Resumen Ejecutivo
El presente reporte técnico describe el diseño, desarrollo e implementación de una Plataforma Legal Inteligente que aprovecha la arquitectura **GraphRAG (Graph Retrieval-Augmented Generation)** y un ecosistema Multi-Agente orquestado por LangGraph. La plataforma permite la ingesta, indexación y consulta conversacional de documentos jurídicos complejos, garantizando cero alucinaciones mediante la extracción estructurada de entidades en una base de datos de grafos (Neo4j).

## 2. Introducción
Los sistemas RAG tradicionales (VectorRAG) presentan limitaciones al tratar de establecer relaciones lógicas inter-documento. Cuando se analizan leyes, códigos o reglamentos institucionales, es crucial no solo recuperar párrafos semánticamente similares, sino comprender la jerarquía y dependencia entre normativas, autoridades y obligaciones. Para solucionar este problema, se diseñó este sistema basado en Grafos de Conocimiento (Knowledge Graphs), donde las "Entidades" y sus "Relaciones" conforman el motor principal de búsqueda y deducción lógica.

## 3. Metodología y Arquitectura
El sistema opera bajo una arquitectura pipeline de tres fases principales:

1.  **Ingesta y Procesamiento (Chunking):** Los documentos PDF o DOCX son divididos en fragmentos (chunks) de longitud controlada (aprox. 600 caracteres) mediante `RecursiveCharacterTextSplitter`.
2.  **Extracción de Grafos Asistida por IA:** Cada fragmento es analizado por el modelo LLM (`gpt-4o-mini`). A través de *prompt engineering*, se extrae un JSON estructurado que mapea las entidades (Personas, Leyes, Conceptos) y las relaciones lógicas (APPLIES_TO, DEFINES, HAS_OBLIGATION) contenidas en el texto.
3.  **Persistencia y Fusión (Merge):** Las entidades se inyectan en AuraDB (Neo4j). Las entidades idénticas de diferentes documentos se fusionan en un solo nodo central, logrando que los documentos se relacionen y conecten automáticamente entre sí.
4.  **Agente Consultor (LangGraph):** El usuario interactúa con un Autómata Finito (StateGraph). Aunque conceptualmente es un solo "Agente Consultor", su cerebro interno se compone de 4 nodos colaborativos (sub-funciones): un Analizador de intenciones, un Buscador Local, un Buscador Global y un Generador de respuestas. Estos 4 nodos comparten una **Memoria a Corto Plazo** (`AgentState`, que almacena temporalmente la plática actual y se borra al cerrar sesión), mientras que Neo4j funge como su memoria a largo plazo (permanente).

## 4. Tecnologías y Herramientas Utilizadas (Stack)
- **Framework de Frontend:** Streamlit (Python).
- **Orquestación de Agentes:** LangChain y LangGraph.
- **Modelos de Lenguaje (LLMs):** OpenAI (`gpt-4o-mini`) para extracción de datos y generación de respuestas.
- **Base de Datos:** Neo4j (AuraDB en la nube) con conectividad mediante el driver oficial de Python.
- **Visualización de Grafos:** PyVis (Renderizado 3D de red impulsado por física).
- **Procesamiento de Archivos:** PyPDF2 y python-docx.

## 5. Resultados Preliminares
- **Eliminación de Alucinaciones:** Durante las pruebas con normatividades institucionales, el agente rechazó exitosamente responder consultas ajenas al corpus documental, limitándose estrictamente al contenido extraído en el grafo.
- **Descubrimiento de Conexiones Lógicas:** El sistema demostró capacidad deductiva; por ejemplo, conectando los principios del *Código de Ética* con las jerarquías y dependencias descritas en la *Ley Orgánica*, aunque estuviesen en documentos separados.
- **Rendimiento Financiero:** La estrategia de procesamiento masivo hacia el grafo probó ser altamente eficiente, consumiendo escasos recursos financieros en tokens de OpenAI (menos de $0.10 USD por cada ~130,000 tokens procesados).

## 6. Discusión
La arquitectura GraphRAG básica implementada demostró una superioridad notable sobre los modelos de chat simples al entender la "estructura" de la ley. Sin embargo, se identificó que la estricta dependencia en búsquedas Cypher (búsqueda literal de palabras clave o descripciones en los nodos) puede resultar limitante cuando el usuario emplea sinónimos complejos. Para mitigar esto, se implementó una rutina de *fallback* automático, demostrando que el diseño de agentes reactivos (LangGraph) aporta gran resiliencia al sistema.

## 7. Perspectivas a Futuro (Next Steps)
Para escalar la plataforma a un nivel de producción empresarial Premium, se proyectan las siguientes fases:
1.  **Modelo Híbrido (GraphRAG + VectorRAG):** Integrar una base de datos vectorial (ej. Pinecone o Chroma) junto a Neo4j. Un Agente Híbrido cruzará la precisión conceptual del Grafo con la recuperación exacta de párrafos textuales (semántica vectorial) para emitir citas textuales impecables.
2.  **Integración de IA Multimodal (Audio):** Implementación de Speech-to-Text (OpenAI Whisper) y Text-to-Speech para que la interacción pueda darse mediante dictado por voz y respuestas habladas.
3.  **Seguridad y Control de Acceso (RBAC):** Autenticación de usuarios para que distintos abogados tengan acceso a distintos espacios de grafos.
4.  **Ingesta de Texto Puro (.txt) Pre-procesado:** Aunque el sistema extrae automáticamente el texto de PDFs y documentos Word de forma invisible, el formato PDF suele generar extracciones sucias (tablas cruzadas, saltos de línea erróneos) que confunden a la IA y deforman el Grafo. Permitir la carga de archivos de texto plano purificados garantizará un Grafo de Conocimiento infinitamente más perfecto, certero y sin pérdida de relaciones clave.

## 8. Conclusión
La implementación de GraphRAG orquestada mediante LangGraph representa un cambio de paradigma en la automatización jurídica. Al convertir documentos legales planos en redes de conocimiento interconectadas, la Inteligencia Artificial adquiere la capacidad no solo de "leer", sino de "entender" y "vincular" el marco normativo, garantizando precisión, trazabilidad y nulo riesgo de alucinación.
