from neo4j import Driver
from typing import List, Dict
from app.db.neo4j_connection import get_neo4j_driver

def recommend_phones_for_user(user_id: str) -> List[Dict]:
    driver: Driver = get_neo4j_driver()

    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_PREFERENCES]->(pref:Preferences)
        MATCH (p:Phone)
        OPTIONAL MATCH (other:User)-[r:RATED]->(p)
        WITH p, pref,
            avg(r.stars) AS avg_rating,
            CASE WHEN abs(p.storage - pref.preferred_storage) <= 32 THEN 1 ELSE 0 END +
            CASE WHEN abs(p.screen_size - pref.preferred_screen_size) <= 0.5 THEN 1 ELSE 0 END +
            CASE WHEN p.camera_quality = pref.preferred_camera THEN 1 ELSE 0 END +
            CASE WHEN p.battery_life = pref.preferred_battery THEN 1 ELSE 0 END +
            CASE WHEN p.design_size = pref.preferred_design THEN 1 ELSE 0 END +
            CASE 
                WHEN pref.preferred_price_range = "low" AND p.price < 200 THEN 1
                WHEN pref.preferred_price_range = "medium" AND p.price >= 200 AND p.price <= 500 THEN 1
                WHEN pref.preferred_price_range = "high" AND p.price > 500 THEN 1
                ELSE 0
            END +
            CASE WHEN p.software = pref.preferred_software THEN 1 ELSE 0 END AS compatibility_score
        WITH p, compatibility_score, coalesce(avg_rating, 0) AS avg_rating
        RETURN p {
            .id,
            .name,
            .brand,
            .price,
            .storage,
            .screen_size,
            .camera_quality,
            .battery_life,
            .design_size,
            .software
        } AS phone,
        compatibility_score,
        avg_rating
        ORDER BY compatibility_score DESC, avg_rating DESC
        LIMIT 10
        """

        result = session.run(query, user_id=user_id)
        recommendations = []

        for record in result:
            phone = record["phone"]
            phone["compatibility_score"] = record["compatibility_score"]
            phone["avg_rating"] = round(record["avg_rating"], 2)
            recommendations.append(phone)

        return recommendations
