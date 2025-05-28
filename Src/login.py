from neo4j import GraphDatabase
from dotenv import load_dotenv

# carga de informacion dotenv
load_dotenv()

# ingreso de credenciales de la base de datos.
uri = input("URI de Neo4j: ")
user_db = input("Usuario de Neo4j: ")
password_db = input("Contraseña: ")

driver = GraphDatabase.driver(uri, auth=(user_db, password_db))

# Verificar si el usuario ya esta dentro de la db.
def verficar_login(tx, usuario, clave):
    query = (
        "MATCH (u:Usuario {usuario: $usuario, contraseña: $contrasena}) "
        "RETURN u.usuario AS usuario"
    )

    result = tx.run(query, usuario=usuario, clave=clave)
    record = result.single()
    return record["usuario"] if record else None

# Login del usuario
def login(usuario, clave):
    with driver.session() as session:
        result = session.read_transaction(verficar_login, usuario, clave)

        if result:
            print("bienvenido{result}")
        else:
            print("Usuario o contraseña incorrectos.")

usuario_input = input("Usuario: ")
clave_input = input("Contraseña: ")
login(usuario_input, clave_input)

# Cerrar sesion
driver.close()