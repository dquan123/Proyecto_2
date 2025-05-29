import sys
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import networkx as nx

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

# Inicio de Sesion
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

    G = nx.Digraph()

    # Nodos
    usuarios = ["U1", "U2"]
    preferencias = ["buena cámara", "buena batería", "pantalla grande"]
    caracteristicas = ["5000mAh", "6.7 pulgadas", "50MP"]
    modelos = ["4000", "9000"]
    marcas = ["Samsung", "Apple"]
    
    # Agregar nodos
    G.add_nodes_from(usuarios + preferencias + caracteristicas + modelos + marcas)

    # Aristas
    G.add_edge("U1", "buena cámara", relation="prefiere")
    G.add_edge("U1", "5000mAh", relation="prefiere")
    G.add_edge("U1", "buena batería", relation="busca")
    G.add_edge("U2", "pantalla grande", relation="busca")
    G.add_edge("U2", "buena batería", relation="prefiere")

    G.add_edge("4000", "Samsung", relation="es_de_la_marca")
    G.add_edge("9000", "Apple", relation="es_de_la_marca")

    G.add_edge("4000", "5000mAh", relation="tiene")
    G.add_edge("4000", "50MP", relation="tiene")
    G.add_edge("9000", "6.7 pulgadas", relation="tiene")

    G.add_edge("5000mAh", "buena batería", relation="califica")
    G.add_edge("6.7 pulgadas", "pantalla grande", relation="califica")
    G.add_edge("50MP", "buena cámara", relation="califica")


if __name__ == "__main__":
    main()
    driver.close()