import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.neo4j_connection import get_neo4j_driver  # Mueve esta línea aquí abajo

driver = get_neo4j_driver()

with driver.session() as session:
    result = session.run("MATCH (p:Phone) RETURN p.name AS name LIMIT 5")
    for record in result:
        print("Teléfono:", record["name"])
