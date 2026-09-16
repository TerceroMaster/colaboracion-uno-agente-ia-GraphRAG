import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jManager:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        if parameters is None:
            parameters = {}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def create_document(self, doc_id, filename, category="General", summary="", page_count=0, chunk_count=0):
        query = """
        MERGE (d:Document {id: $doc_id})
        SET d.filename = $filename, 
            d.category = $category,
            d.summary = $summary,
            d.page_count = $page_count,
            d.chunk_count = $chunk_count
        RETURN d
        """
        self.execute_query(query, {
            "doc_id": doc_id, 
            "filename": filename, 
            "category": category,
            "summary": summary,
            "page_count": page_count,
            "chunk_count": chunk_count
        })

    def delete_document(self, doc_id):
        # Primero borra los chunks asociados al documento
        query_chunks = """
        MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)
        DETACH DELETE c
        """
        self.execute_query(query_chunks, {"doc_id": doc_id})
        
        # Luego borra el documento
        query_doc = """
        MATCH (d:Document {id: $doc_id})
        DETACH DELETE d
        """
        self.execute_query(query_doc, {"doc_id": doc_id})

    def create_chunk(self, chunk_id, doc_id, text, chunk_index):
        query = """
        MATCH (d:Document {id: $doc_id})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text, c.index = $chunk_index
        MERGE (d)-[:HAS_CHUNK]->(c)
        RETURN c
        """
        self.execute_query(query, {"chunk_id": chunk_id, "doc_id": doc_id, "text": text, "chunk_index": chunk_index})

    def create_entity(self, entity_name, entity_type, description):
        query = """
        MERGE (e:Entity {name: $entity_name})
        SET e.type = $entity_type, e.description = $description
        RETURN e
        """
        self.execute_query(query, {"entity_name": entity_name, "entity_type": entity_type, "description": description})

    def create_relationship(self, source_name, target_name, rel_type, description):
        query = """
        MATCH (s:Entity {name: $source_name})
        MATCH (t:Entity {name: $target_name})
        MERGE (s)-[r:RELATED_TO {type: $rel_type}]->(t)
        SET r.description = $description
        RETURN r
        """
        self.execute_query(query, {"source_name": source_name, "target_name": target_name, "rel_type": rel_type, "description": description})

    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)

    def get_graph_stats(self):
        query = """
        MATCH (n)
        WITH count(n) AS node_count
        MATCH ()-[r]->()
        RETURN node_count, count(r) AS rel_count
        """
        try:
            results = self.execute_query(query)
            if results:
                return results[0]
            return {"node_count": 0, "rel_count": 0}
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"node_count": 0, "rel_count": 0}
