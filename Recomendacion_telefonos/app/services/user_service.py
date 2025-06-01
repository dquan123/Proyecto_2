from neo4j import Driver

def create_user(user_id: str, name: str, driver: Driver) -> str:
    query = """
    MERGE (u:User {id: $user_id})
    ON CREATE SET u.name = $name
    ON MATCH SET u.name = $name
    RETURN u
    """

    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, name=name)
            record = result.single()
            if record:
                return f"Usuario '{user_id}' creado o actualizado correctamente."
            else:
                return "No se pudo crear el usuario."
    except Exception as e:
        return f"Error al crear usuario: {e}"
