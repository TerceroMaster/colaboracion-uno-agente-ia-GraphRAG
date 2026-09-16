import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class GraphExtractor:
    def __init__(self, model_name="gpt-4o-mini"):
        # We use a model capable of JSON output. gpt-4o-mini is efficient and capable.
        api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
        self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, model_kwargs={"response_format": {"type": "json_object"}})
        
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal data extraction expert. 
Extract entities and relationships from the provided text.
Entities should be of types: Person, Organization, Law, Concept, Document, Date, Location.
Relationships should specify how entities are connected (e.g., 'APPLIES_TO', 'MENTIONS', 'DEFINES', 'PARTICIPATES_IN').

Output exactly in this JSON format:
{{
  "entities": [
    {{"name": "Entity Name", "type": "Entity Type", "description": "Brief description of the entity in this context"}}
  ],
  "relationships": [
    {{"source": "Source Entity Name", "target": "Target Entity Name", "type": "RELATIONSHIP_TYPE", "description": "Explanation of the connection"}}
  ]
}}
If no entities or relationships are found, return empty lists.
"""),
            ("user", "Text to analyze:\n{text}")
        ])
        
        self.chain = self.extraction_prompt | self.llm

    def extract(self, text):
        try:
            response = self.chain.invoke({"text": text})
            # Parse the JSON response
            content = response.content
            return json.loads(content)
        except Exception as e:
            print(f"Extraction failed: {e}")
            return {"entities": [], "relationships": []}
