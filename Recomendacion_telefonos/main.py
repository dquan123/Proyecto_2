import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import Frame, Label, Scrollbar, Canvas, VERTICAL, RIGHT, Y, BOTH
from neo4j import GraphDatabase
from dotenv import load_dotenv
from app.services.user_service import create_user
from app.services.rating_service import add_rating
from app.services.preferences_service import create_user_preferences


# Carga de variables de entorno
load_dotenv()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.recommendation_service import recommend_phones_for_user

class PhoneRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conectar a Neo4j")
        self.driver = None

        self.setup_conexion_ui()

    def setup_conexion_ui(self):
        tk.Label(self.root, text="URI de Neo4j").pack()
        self.uri_entry = tk.Entry(self.root, width=40)
        self.uri_entry.pack()
        self.uri_entry.insert(0, "bolt://localhost:7687")

        tk.Label(self.root, text="Usuario").pack()
        self.user_entry = tk.Entry(self.root, width=40)
        self.user_entry.pack()
        self.user_entry.insert(0, "admin")

        tk.Label(self.root, text="Contraseña").pack()
        self.pass_entry = tk.Entry(self.root, show="*", width=40)
        self.pass_entry.pack()
        self.pass_entry.insert(0, "aaaaaaaa")

        tk.Button(self.root, text="Conectar", command=self.conectar_a_neo4j).pack(pady=10)

    def conectar_a_neo4j(self):
        uri = self.uri_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            messagebox.showinfo("Éxito", "Conexión exitosa a Neo4j")
            self.mostrar_interfaz_recomendaciones()
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar: {e}")

    def mostrar_interfaz_recomendaciones(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Sistema de Recomendación de Teléfonos 📱")

        tk.Label(self.root, text="ID de usuario").pack()
        self.id_entry = tk.Entry(self.root, width=40)
        self.id_entry.pack()

        tk.Button(self.root, text="Mostrar Recomendaciones", command=self.mostrar_recomendaciones).pack(pady=5)
        tk.Button(self.root, text="Crear/Actualizar Usuario", command=self.crear_usuario).pack(pady=2)
        tk.Button(self.root, text="Crear Preferencias", command=self.definir_preferencias).pack(pady=2)
        tk.Button(self.root, text="Calificar Teléfono", command=self.calificar_telefono).pack(pady=2)

        # Contenedor de recomendaciones
        self.canvas = Canvas(self.root)
        self.scrollbar = Scrollbar(self.root, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

    def mostrar_recomendaciones(self):
        user_id = self.id_entry.get().strip()

        # Limpiar resultados anteriores
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            recomendaciones = recommend_phones_for_user(user_id)

            if not recomendaciones:
                tk.Label(self.scrollable_frame, text="No se encontraron recomendaciones para este usuario.").pack()
            else:
                for idx, phone in enumerate(recomendaciones, start=1):
                    card = Frame(self.scrollable_frame, bd=2, relief="groove", padx=10, pady=5)
                    Label(card, text=f"{idx}. {phone['name']} ({phone['brand']})", font=("Arial", 12, "bold")).pack(anchor="w")
                    Label(card, text=f"Precio: ${phone['price']}", anchor="w").pack(anchor="w")
                    Label(card, text=f"Pantalla: {phone['screen_size']} in", anchor="w").pack(anchor="w")
                    Label(card, text=f"Almacenamiento: {phone['storage']} GB", anchor="w").pack(anchor="w")
                    Label(card, text=f"Cámara: {phone['camera_quality']}, Batería: {phone['battery_life']}", anchor="w").pack(anchor="w")
                    Label(card, text=f"Compatibilidad: {phone['compatibility_score']}/7", anchor="w").pack(anchor="w")
                    Label(card, text=f"Rating promedio: {phone['avg_rating']}/5", anchor="w").pack(anchor="w")
                    card.pack(fill=BOTH, expand=True, pady=5, padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Falló al obtener recomendaciones: {e}")
        
    def crear_usuario(self):
        popup = tk.Toplevel(self.root)
        popup.title("Crear Nuevo Usuario")
        popup.geometry("300x200")

        tk.Label(popup, text="ID de Usuario:").pack(pady=5)
        id_entry = tk.Entry(popup)
        id_entry.pack(pady=5)

        tk.Label(popup, text="Nombre del Usuario:").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        def confirmar_creacion():
            user_id = id_entry.get().strip()
            name = name_entry.get().strip()

            if not user_id or not name:
                messagebox.showwarning("Campos incompletos", "Por favor llena ambos campos.")
                return

            mensaje = create_user(user_id, name, self.driver)
            messagebox.showinfo("Resultado", mensaje)
            popup.destroy()

        tk.Button(popup, text="Crear Usuario", command=confirmar_creacion).pack(pady=15)
        

    def calificar_telefono(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Calificar Teléfono")

        # Obtener todos los teléfonos disponibles
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (p:Phone) RETURN p.id AS id, p.name AS name ORDER BY p.name")
                telefonos = result.data()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los teléfonos: {str(e)}")
            return

        if not telefonos:
            messagebox.showinfo("Info", "No hay teléfonos registrados.")
            return

        # Mostrar lista numerada
        lista_texto = "\n".join([f"{i+1}. {t['name']} (ID: {t['id']})" for i, t in enumerate(telefonos)])

        tk.Label(ventana, text="ID del Usuario (ej. u1):").grid(row=0, column=0)
        user_id_entry = tk.Entry(ventana)
        user_id_entry.grid(row=0, column=1)

        tk.Label(ventana, text="Selecciona un teléfono:").grid(row=1, column=0, sticky="w")
        tk.Label(ventana, text=lista_texto, justify="left").grid(row=2, column=0, columnspan=2, sticky="w")

        tk.Label(ventana, text="Número de la lista:").grid(row=3, column=0)
        seleccion_entry = tk.Entry(ventana)
        seleccion_entry.grid(row=3, column=1)

        tk.Label(ventana, text="Estrellas (1 a 5):").grid(row=4, column=0)
        stars_entry = tk.Entry(ventana)
        stars_entry.grid(row=4, column=1)

        def guardar_calificacion():
            user_id = user_id_entry.get().strip()
            try:
                index = int(seleccion_entry.get()) - 1
                stars = float(stars_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa valores válidos.")
                return

            if index < 0 or index >= len(telefonos):
                messagebox.showerror("Error", "Número de teléfono inválido.")
                return

            if stars < 1 or stars > 5:
                messagebox.showerror("Error", "La calificación debe estar entre 1 y 5.")
                return

            phone_id = telefonos[index]['id']
            mensaje = add_rating(user_id, phone_id, stars, self.driver)
            messagebox.showinfo("Resultado", mensaje)
            ventana.destroy()

        tk.Button(ventana, text="Guardar Calificación", command=guardar_calificacion).grid(row=5, columnspan=2, pady=10)
        
    def definir_preferencias(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Definir Preferencias")

        # Campos de entrada
        tk.Label(ventana, text="ID del Usuario:").grid(row=0, column=0)
        user_id_entry = tk.Entry(ventana)
        user_id_entry.grid(row=0, column=1)

        # Opciones desplegables
        opciones_disenio = ["small", "medium", "large"]
        opciones_precio = ["low", "medium", "high"]
        opciones_bateria = ["short", "medium", "long"]
        opciones_camara = ["low", "medium", "high"]
        opciones_software = ["Android", "iOS"]

        # Campos de selección
        def crear_selector(texto, opciones, fila):
            tk.Label(ventana, text=texto).grid(row=fila, column=0)
            var = tk.StringVar()
            var.set(opciones[0])
            menu = tk.OptionMenu(ventana, var, *opciones)
            menu.grid(row=fila, column=1)
            return var

        diseño_var = crear_selector("Diseño:", opciones_disenio, 1)
        precio_var = crear_selector("Rango de Precio:", opciones_precio, 2)
        bateria_var = crear_selector("Batería:", opciones_bateria, 3)
        camara_var = crear_selector("Cámara:", opciones_camara, 4)
        software_var = crear_selector("Software:", opciones_software, 5)

        tk.Label(ventana, text="Almacenamiento (número en GB):").grid(row=6, column=0)
        almacenamiento_entry = tk.Entry(ventana)
        almacenamiento_entry.grid(row=6, column=1)

        tk.Label(ventana, text="Tamaño de Pantalla (por ejemplo 6.1):").grid(row=7, column=0)
        pantalla_entry = tk.Entry(ventana)
        pantalla_entry.grid(row=7, column=1)

        def guardar_preferencias():
            user_id = user_id_entry.get().strip()
            try:
                storage = int(almacenamiento_entry.get())
                screen = float(pantalla_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Almacenamiento y pantalla deben ser números.")
                return

            mensaje = create_user_preferences(
                user_id=user_id,
                preferences={
                    "preferred_design": diseño_var.get(),
                    "preferred_storage": storage,
                    "preferred_price_range": precio_var.get(),
                    "preferred_screen_size": screen,
                    "preferred_software": software_var.get(),
                    "preferred_battery": bateria_var.get(),
                    "preferred_camera": camara_var.get(),
                },
                driver=self.driver
            )
            messagebox.showinfo("Resultado", mensaje)
            ventana.destroy()

        tk.Button(ventana, text="Guardar Preferencias", command=guardar_preferencias).grid(row=8, columnspan=2, pady=10)





if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneRecommenderApp(root)
    root.mainloop()
