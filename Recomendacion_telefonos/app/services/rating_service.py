from app.db.neo4j_connection import get_neo4j_driver

def add_rating(user_id: str, phone_id: str, stars: int):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id}), (p:Phone {id: $phone_id})
        MERGE (u)-[r:RATED]->(p)
        SET r.stars = $stars
        """
        session.run(query, user_id=user_id, phone_id=phone_id, stars=stars)
