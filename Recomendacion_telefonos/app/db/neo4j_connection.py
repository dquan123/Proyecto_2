from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687" 
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_neo4j_driver():
    return _driver
