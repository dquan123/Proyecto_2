import sys
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# carga de informacion dotenv
load_dotenv()

# ingreso de credenciales de la base de datos.
uri = input("URI de Neo4j: ")
user_db = input("Usuario de Neo4j: ")
password_db = input("Contraseña: ")

driver = GraphDatabase.driver(uri, auth=(user_db, password_db))

# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.recommendation_service import recommend_phones_for_user
def verificar_login(tx, id, usuario):
    query = (

    )

    result = tx.run(query, usuario=usuario, id = id)
    record = result.single()
    return record["usuario"] if record else None

def login(usuario, id):
    with driver.session() as session:
        result = session.read_transaction(verificar_login, usuario, id)
        if result:
            print(f"Bienvenido, {result}!\n")
            return True
        else:
            print("Usuario o contraseña incorrectos.\n")
            return False

def main():
    print("Bienvenido al Sistema de Recomendación de Teléfonos 📱")
    user_id = input("Ingrese su ID de usuario: ").strip()

    try:
        recomendaciones = recommend_phones_for_user(user_id)

        if not recomendaciones:
            print("No se encontraron recomendaciones para este usuario.")
        else:
            print("\n Teléfonos recomendados:")
            for idx, phone in enumerate(recomendaciones, start=1):
                print(f"{idx}. {phone}")
    except Exception as e:
        print("Error al obtener recomendaciones:", e)

if __name__ == "__main__":
    main()
    driver.close()