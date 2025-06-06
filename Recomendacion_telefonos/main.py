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
            recomendaciones = recommend_phones_for_user(user_id, self.driver)

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
        ventana.geometry("500x400")  # Tamaño fijo para la ventana
        
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

        # Frame principal
        main_frame = Frame(ventana)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Campos de entrada en la parte superior
        tk.Label(main_frame, text="ID del Usuario (ej. u1):").pack(anchor="w")
        user_id_entry = tk.Entry(main_frame, width=30)
        user_id_entry.pack(anchor="w", pady=(0, 10))

        tk.Label(main_frame, text="Selecciona un teléfono:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Frame para el área con scroll
        scroll_frame = Frame(main_frame)
        scroll_frame.pack(fill=BOTH, expand=True, pady=(5, 10))
        
        # Canvas y scrollbar para la lista de teléfonos
        canvas = Canvas(scroll_frame, height=200)
        scrollbar = Scrollbar(scroll_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_phone_frame = Frame(canvas)
        
        scrollable_phone_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_phone_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variable para almacenar la selección
        seleccion_var = tk.StringVar()
        
        # Crear radio buttons para cada teléfono
        for i, telefono in enumerate(telefonos):
            radio_frame = Frame(scrollable_phone_frame)
            radio_frame.pack(fill="x", padx=5, pady=2)
            
            radio_btn = tk.Radiobutton(
                radio_frame, 
                text=f"{telefono['name']} (ID: {telefono['id']})",
                variable=seleccion_var,
                value=str(i),
                wraplength=400,
                justify="left"
            )
            radio_btn.pack(anchor="w")
        
        # Configurar el scroll con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para la calificación
        rating_frame = Frame(main_frame)
        rating_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(rating_frame, text="Calificación (1 a 5 estrellas):").pack(anchor="w")
        stars_entry = tk.Entry(rating_frame, width=10)
        stars_entry.pack(anchor="w")
        
        # Función para guardar la calificación
        def guardar_calificacion():
            user_id = user_id_entry.get().strip()
            seleccion = seleccion_var.get()
            
            if not user_id:
                messagebox.showerror("Error", "Por favor ingresa el ID del usuario.")
                return
                
            if not seleccion:
                messagebox.showerror("Error", "Por favor selecciona un teléfono.")
                return
            
            try:
                stars = float(stars_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa una calificación válida.")
                return

            if stars < 1 or stars > 5:
                messagebox.showerror("Error", "La calificación debe estar entre 1 y 5.")
                return

            try:
                index = int(seleccion)
                phone_id = telefonos[index]['id']
                mensaje = add_rating(user_id, phone_id, stars, self.driver)
                messagebox.showinfo("Resultado", mensaje)
                ventana.destroy()
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Selección de teléfono inválida.")

        # Botón para guardar
        tk.Button(main_frame, text="Guardar Calificación", command=guardar_calificacion, 
                bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)        
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
