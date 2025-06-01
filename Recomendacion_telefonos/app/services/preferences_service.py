def create_user_preferences(user_id, preferences, driver):
    try:
        with driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (p:Preferences {
                preferred_design: $design,
                preferred_storage: $storage,
                preferred_price_range: $price_range,
                preferred_screen_size: $screen_size,
                preferred_software: $software,
                preferred_battery: $battery,
                preferred_camera: $camera
            })
            CREATE (u)-[:HAS_PREFERENCES]->(p)
            """
            session.run(query, {
                "user_id": user_id,
                "design": preferences["preferred_design"],
                "storage": preferences["preferred_storage"],
                "price_range": preferences["preferred_price_range"],
                "screen_size": preferences["preferred_screen_size"],
                "software": preferences["preferred_software"],
                "battery": preferences["preferred_battery"],
                "camera": preferences["preferred_camera"]
            })
        return "Preferencias guardadas correctamente."
    except Exception as e:
        return f"Error al guardar preferencias: {str(e)}"
