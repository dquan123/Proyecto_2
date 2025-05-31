from neo4j import Driver
from typing import List, Dict
from app.db.neo4j_connection import get_neo4j_driver

def recommend_phones_for_user(user_id: str):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_PREFERENCES]->(pref:Preferences)
        MATCH (p:Phone)-[:OF_BRAND]->(brand:Brand)
        OPTIONAL MATCH (other:User)-[r:RATED]->(p)
        OPTIONAL MATCH (p2:Phone)-[:OF_BRAND]->(brand)
        OPTIONAL MATCH (u)-[r2:RATED]->(p2)
        
        WITH u, p, pref, brand, avg(r.stars) AS avg_rating,
            avg(r2.stars) AS user_brand_avg

        // Coincidencias con preferencias
        WITH p, pref, avg_rating, user_brand_avg,
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

        // Ponderación por afinidad con marca
        WITH p, compatibility_score, coalesce(avg_rating, 0) AS avg_rating,
             CASE 
                WHEN user_brand_avg >= 4 THEN 1
                WHEN user_brand_avg < 3 THEN -1
                ELSE 0
             END AS brand_affinity

        // Calcular puntaje final
        WITH p, compatibility_score, avg_rating, brand_affinity,
             (compatibility_score * 2 + brand_affinity + (avg_rating / 5.0) * 2) AS total_score

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
        avg_rating,
        brand_affinity,
        total_score
        ORDER BY total_score DESC
        LIMIT 10
        """

        result = session.run(query, user_id=user_id)
        recommendations = []

        for record in result:
            phone = record["phone"]
            phone["compatibility_score"] = record["compatibility_score"]
            phone["avg_rating"] = round(record["avg_rating"], 2)
            phone["brand_affinity"] = record["brand_affinity"]
            phone["total_score"] = round(record["total_score"], 2)
            recommendations.append(phone)

        return recommendations
