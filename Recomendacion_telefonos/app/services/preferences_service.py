from app.db.neo4j_connection import get_neo4j_driver
from app.models.preferences import Preferences

def create_user_preferences(user_id: str, preferences: Preferences):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})
        CREATE (p:Preferences {
            preferred_storage: $preferred_storage,
            preferred_screen_size: $preferred_screen_size,
            preferred_camera: $preferred_camera,
            preferred_battery: $preferred_battery,
            preferred_design: $preferred_design,
            preferred_price_range: $preferred_price_range,
            preferred_software: $preferred_software
        })
        CREATE (u)-[:HAS_PREFERENCES]->(p)
        """
        session.run(query, **preferences.dict())
