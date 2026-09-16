# Entendiendo el Procesamiento y Costo de GraphRAG

A diferencia de los sistemas RAG (Retrieval-Augmented Generation) tradicionales que simplemente convierten el texto en vectores matemáticos de forma masiva, **GraphRAG** requiere que una Inteligencia Artificial "lea" y "comprenda" el texto para construir un mapa mental (un Grafo de Conocimiento). 

Este proceso es más intensivo, pero garantiza respuestas precisas y libres de alucinaciones. A continuación se explica detalladamente cómo funciona este proceso bajo el capó.

---

## 1. División del texto en fragmentos (Chunks)

El código no le pasa el PDF entero al LLM (Large Language Model) de una sola vez. En su lugar, corta el texto en pedacitos pequeños, conocidos como *chunks*. 

En nuestra configuración actual, el tamaño es de **600 caracteres**.

**Ejemplo de un Chunk:**
> *"ARTÍCULO 1.- Las disposiciones de este Código son de observancia general y obligatoria para las autoridades universitarias, profesores, investigadores, estudiantes y personal administrativo de la Universidad Juárez Autónoma de Tabasco. Tiene como propósito fundamental establecer los principios éticos que deben guiar el comportamiento..."*

---

## 2. Petición individual al LLM por cada Chunk

Por cada uno de estos pedacitos de texto, el sistema hace una petición (Request) al modelo `gpt-4o-mini` a través de la API de OpenAI.

**Instrucción enviada al LLM:**
> "Lee este fragmento de texto legal y extrae en formato JSON todas las entidades (Personas, Organizaciones, Leyes, Conceptos) y las relaciones entre ellas."

**Respuesta del LLM (JSON devuelto):**
```json
{
  "entities": [
    {"name": "Código", "type": "Document", "description": "Código de ética de observancia general."},
    {"name": "Universidad Juárez Autónoma de Tabasco", "type": "Organization", "description": "Institución de educación superior."}
  ],
  "relationships": [
    {"source": "Código", "target": "Universidad Juárez Autónoma de Tabasco", "type": "APPLIES_TO", "description": "El código es de observancia obligatoria para los miembros de la universidad."}
  ]
}
```

---

## 3. La Matemática del Consumo (Tokens y Requests)

Cada vez que el LLM lee las instrucciones, lee el fragmento y genera el JSON de respuesta, está consumiendo **tokens**.

*   **1 Chunk = 1 Petición (Request)**
*   Instrucciones del sistema + Chunk de texto ≈ 300 tokens de entrada (Input).
*   Generación del JSON por el LLM ≈ 200 tokens de salida (Output).
*   **Total por Chunk ≈ 500 tokens.**

Si subimos los 3 documentos de prueba (Código de Ética, UJAT202203 y Ley Orgánica), que juntos generan alrededor de **304 fragmentos**, la matemática final y real se ve así en el panel de consumo de OpenAI:

1.  **Total de Peticiones:** 304 requests.
2.  **Consumo de Tokens:** ~134,131 tokens totales.
3.  **Tiempo de ejecución:** Aproximadamente 15-20 minutos (debido al procesamiento secuencial).

> [!TIP]
> **¿Es caro?**
> A pesar de que los números de tokens suenan masivos, el modelo `gpt-4o-mini` es extremadamente económico. El procesamiento real de estos 134 mil tokens (leyendo y procesando 3 PDFs completos para convertirlos en grafo) tuvo un costo exacto de **$0.09 dólares (9 centavos)**. El valor real de GraphRAG radica en que esta pequeña inversión de 9 centavos genera una base de datos de conocimiento perfecta para que ahora las consultas futuras sean inmediatas, precisas y cuesten solo fracciones de centavo.

---

## 4. ¿Cómo recupera la información el Agente IA?

Cuando haces una pregunta (ej. *"¿De qué trata la SECCIÓN TERCERA?"*), el agente no busca en los PDFs ni en el texto crudo, sino que entra al **Grafo de Conocimiento alojado en Neo4j** y encuentra el "mapa conceptual" extraído previamente, algo como esto:

`[Entidad: SECCIÓN TERCERA] ---> (TRATA_SOBRE) ---> [Responsabilidad en uso de recursos]`
`[Autoridades] ---> (DEBEN_ACTUAR) ---> [Con integridad y transparencia]`

El agente toma ese mapa, lo lee y redacta una respuesta fluida para ti basada *exclusivamente* en esas conexiones lógicas. 

### ¿Por qué no cita el texto exacto del PDF?
En esta implementación básica de GraphRAG, el LLM extrajo el "jugo" (entidades y relaciones) y **eso fue lo único que nuestro agente guardó y configuró para consultar**. Como ya no tiene acceso al texto original crudo al momento de responder, hace un resumen conceptual perfecto en lugar de hacer un "copia y pega" de los artículos de la ley.

### ¿Se puede recuperar el texto exacto usando solo GraphRAG?
**¡Sí, es totalmente posible!** La limitante actual no es de GraphRAG, sino de cómo le dijimos al Agente que buscara la información en nuestra base de datos.
De hecho, durante la indexación, nuestro código actual **sí guarda el texto exacto** dentro de un nodo tipo `[Chunk]` en Neo4j. Para lograr que el agente cite textos exactos usando puramente GraphRAG, solo tendríamos que modificar la consulta (Query) del Agente para decirle: 
> *"Además de traerme las entidades y sus relaciones, ve al nodo `[Chunk]` del que salieron y tráeme el texto original."*

### Modelos Híbridos (GraphRAG + Vector RAG) - (Próxima Versión Premium)
Otra alternativa común en la industria, y que será nuestro siguiente paso evolutivo, es crear una arquitectura **Híbrida**. En un modelo híbrido, el sistema utilizará múltiples agentes simultáneos:
1.  Un **Agente Analista (GraphRAG)** buscará en el Grafo (Neo4j) para entender el contexto estructural, las reglas y las relaciones lógicas (evitando alucinaciones).
2.  Un **Agente Documental (VectorRAG)** buscará en una Base de Datos Vectorial por similitud semántica para recuperar el párrafo exacto original.

El sistema orquestador fusionará ambos resultados para darte una respuesta súper contextualizada citando exactamente el artículo y mostrando la lógica jurídica detrás de la respuesta. **La desventaja:** Construir y mantener un modelo híbrido cuesta más (tiempo de desarrollo y costos de base de datos extra) y es más complejo, pero es el estándar de oro absoluto para aplicaciones legales en producción.

---

## 6. La Importancia del Formato (PDF vs Texto Plano) - Trabajo Futuro

Nuestro sistema extrae automáticamente el texto de PDFs y documentos Word de forma invisible antes de enviarlo a la IA para crear el grafo. Sin embargo, **el formato PDF es notoriamente problemático**. Si un PDF legal tiene:
- Tablas complejas.
- Encabezados y pies de página en cada hoja.
- Texto a dos columnas.
- O es un documento escaneado (imágenes en lugar de texto).

La extracción automática suele salir "sucia" (palabras pegadas, saltos de línea erróneos, caracteres basura). **Si el texto plano sale sucio, la IA se confunde y el Grafo de Conocimiento sale deforme o le faltan relaciones clave.**

**Próxima Función (Soporte Nativo .txt):** Para entornos de producción empresarial, implementaremos soporte nativo para carga directa de archivos de **texto plano purificado (`.txt`)**. Si los ingenieros de datos limpian los documentos previamente y se aseguran de que sean texto puro y bien formateado, el Grafo de Conocimiento generado será **infinitamente más perfecto, certero y sin pérdida de información**.

---

## 7. ¿Dónde queda guardada la "Categoría" de los documentos?

Cuando configuramos el Agente Legal, le añadimos una función para asignar categorías (ej. Ley Orgánica, Normativa, Código de Ética). 
La modificación que hicimos en el archivo `neo4j_manager.py` y `1_Agente_Legal.py` le dice a Neo4j: *"Oye, cuando guardes el nodo de tipo `[Document]`, ponle una etiqueta extra que se llame `category` con el valor que escogió el usuario"*. 

Así, esa categorización ya vive directamente como metadato dentro de tu base de datos Neo4j. Esto sirve para futuras consultas, permitiendo filtrar búsquedas solo dentro de una categoría específica en lugar de buscar en toda la base de datos a la vez.
