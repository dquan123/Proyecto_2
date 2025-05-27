import sys
import os

# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.recommendation_service import recommend_phones_for_user

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
