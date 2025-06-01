# app/services/rating_service.py

def add_rating(user_id: str, phone_id: str, stars: int, driver):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id}), (p:Phone {id: $phone_id})
            MERGE (u)-[r:RATED]->(p)
            SET r.stars = $stars
        """, user_id=user_id, phone_id=phone_id, stars=stars)
