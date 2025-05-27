from app.db.neo4j_connection import get_neo4j_driver
from app.models.phone import Phone

def create_phone(phone: Phone):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
        CREATE (p:Phone {
            id: $id,
            name: $name,
            brand: $brand,
            storage: $storage,
            screen_size: $screen_size,
            camera_quality: $camera_quality,
            battery_life: $battery_life,
            design_size: $design_size,
            price: $price,
            software: $software
        })
        """
        session.run(query, **phone.dict())
