import os
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from src.neo4j_manager import Neo4jManager
from dotenv import load_dotenv
import operator

load_dotenv()

# Define the state for LangGraph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    search_strategy: str # 'local', 'global', or 'direct'
    context: str

class GraphRAGAgent:
    def __init__(self, neo4j_manager: Neo4jManager):
        api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        self.neo4j_manager = neo4j_manager
        
        # Build the graph
        workflow = StateGraph(AgentState)
        
        workflow.add_node("analyzer", self.analyze_query)
        workflow.add_node("local_search", self.local_search)
        workflow.add_node("global_search", self.global_search)
        workflow.add_node("generator", self.generate_response)
        
        # Define edges
        workflow.set_entry_point("analyzer")
        
        # Conditional routing based on search strategy
        workflow.add_conditional_edges(
            "analyzer",
            self.route_search,
            {
                "local": "local_search",
                "global": "global_search",
                "direct": "generator"
            }
        )
        
        workflow.add_edge("local_search", "generator")
        workflow.add_edge("global_search", "generator")
        workflow.add_edge("generator", END)
        
        self.app = workflow.compile()

    def analyze_query(self, state: AgentState):
        messages = state['messages']
        last_message = messages[-1].content
        
        # Simple analyzer prompt
        analyzer_prompt = f"""
        Analyze the following user query and decide if it requires:
        - "local": specific information about a particular entity, person, or law.
        - "global": thematic summaries, overall trends, or questions spanning many documents.
        - "direct": a simple conversational response not requiring graph search.
        
        Query: {last_message}
        
        Return ONLY the word "local", "global", or "direct".
        """
        
        response = self.llm.invoke([HumanMessage(content=analyzer_prompt)])
        strategy = response.content.strip().lower()
        
        # default to local if unclear
        if strategy not in ["local", "global", "direct"]:
            strategy = "local"
            
        return {"search_strategy": strategy}

    def route_search(self, state: AgentState):
        return state["search_strategy"]

    def local_search(self, state: AgentState):
        query = state['messages'][-1].content
        
        # Extract potential entities from query to search in Neo4j
        extract_prompt = f"Extract the key entities (names, laws, concepts) from this query. Return them as a comma-separated list. Query: {query}"
        entities_response = self.llm.invoke([HumanMessage(content=extract_prompt)])
        entities = [e.strip() for e in entities_response.content.split(',')]
        
        context_parts = []
        for entity in entities:
            # Simple exact match or contains search in Neo4j (case-insensitive)
            cypher = """
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($entity) OR toLower($entity) CONTAINS toLower(e.name)
            OPTIONAL MATCH (e)-[r]->(target)
            OPTIONAL MATCH (source)-[r2]->(e)
            RETURN e.name, e.type, e.description, 
                   type(r) as out_rel, target.name as out_target, target.type as out_type,
                   type(r2) as in_rel, source.name as in_source, source.type as in_type
            LIMIT 50
            """
            results = self.neo4j_manager.execute_query(cypher, {"entity": entity})
            
            for row in results:
                desc = f"Entity: {row['e.name']} ({row['e.type']}) - {row['e.description']}"
                if row.get('out_target'):
                    desc += f"\n  -> {row['out_rel']} -> {row['out_target']} ({row['out_type']})"
                if row.get('in_source'):
                    desc += f"\n  <- {row['in_rel']} <- {row['in_source']} ({row['in_type']})"
                context_parts.append(desc)
                
        context = "\n".join(set(context_parts))
        if not context:
            context = "No specific entities found in the knowledge graph for this query."
            
        return {"context": context}

    def global_search(self, state: AgentState):
        # Para búsqueda global, traemos las 50 entidades más conectadas (más importantes)
        cypher = """
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r]-()
        WITH e, count(r) AS rel_count
        ORDER BY rel_count DESC
        LIMIT 50
        RETURN e.name, e.description
        """
        results = self.neo4j_manager.execute_query(cypher)
        context_parts = []
        for row in results:
            context_parts.append(f"{row['e.name']}: {row['e.description']}")
            
        context = "\n".join(context_parts)
        if not context:
            context = "No global concepts found in the database."
            
        return {"context": f"Global Context:\n{context}"}

    def generate_response(self, state: AgentState):
        messages = state['messages']
        context = state.get('context', '')
        
        system_prompt = f"""
        You are a highly capable legal AI assistant.
        Use the following information retrieved from the knowledge graph to answer the user's query.
        If the information is not present in the context, say "I don't have enough information to answer that." 
        Do not hallucinate.
        
        Context:
        {context}
        """
        
        new_messages = [SystemMessage(content=system_prompt)] + list(messages)
        response = self.llm.invoke(new_messages)
        
        return {"messages": [response]}

    def chat(self, user_input, chat_history=[]):
        messages = chat_history + [HumanMessage(content=user_input)]
        
        # Invoke the graph
        result = self.app.invoke({"messages": messages})
        
        # The result includes the updated messages list
        return result['messages'][-1].content
