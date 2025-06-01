def add_rating(user_id, phone_id, stars, driver):
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id}), (p:Phone {id: $phone_id})
                MERGE (u)-[r:RATED]->(p)
                SET r.stars = $stars
                RETURN u.id, p.name, r.stars
            """, user_id=user_id, phone_id=phone_id, stars=stars)

            record = result.single()
            if record:
                return f"Calificación registrada: {record['r.stars']} estrellas para {record['p.name']}"
            else:
                return "No se encontró el usuario o teléfono."

    except Exception as e:
        return f"Error al calificar: {str(e)}"
