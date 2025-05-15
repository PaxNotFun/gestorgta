import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import sv_ttk
from database import ejecutar_consulta, obtener_datos

# Verificar actualizaciones al iniciar
try:
    import updater
    if updater.actualizar_aplicacion():
        print("Actualización exitosa. Reiniciando...")
        import sys
        import os
        os.execl(sys.executable, sys.executable, "main.py")
except Exception as e:
    print(f"No se pudo actualizar: {str(e)}")

class VentanaCentrada:
    @staticmethod
    def centrar(ventana, ancho=0, alto=0):
        ventana.update_idletasks()
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2) if ancho else (pantalla_ancho - ventana.winfo_width()) // 2
        y = (pantalla_alto // 2) - (alto // 2) if alto else (pantalla_alto - ventana.winfo_height()) // 2
        ventana.geometry(f"+{x}+{y}")

class LoginWindow:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Acceso al Sistema")
        self.root.geometry("400x200")
        VentanaCentrada.centrar(self.root, 400, 200)
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        
        frame = ttk.Frame(self.root)
        frame.pack(pady=30, padx=30, fill="both", expand=True)
        
        ttk.Label(frame, text="🔑 Código de acceso:").pack(pady=10)
        self.codigo_entry = ttk.Entry(frame)
        self.codigo_entry.pack(pady=5, ipadx=30)
        
        ttk.Button(
            frame, 
            text="Ingresar", 
            command=self.verificar_acceso,
            style="Accent.TButton"
        ).pack(pady=15)
        
        self.root.mainloop()
    
    def verificar_acceso(self):
        codigo = self.codigo_entry.get()
        usuario = obtener_datos("SELECT nombre FROM usuarios WHERE codigo = %s", (codigo,))
        
        if usuario:
            self.root.destroy()
            GestorVehiculos(codigo, usuario[0][0])
        else:
            messagebox.showerror("Error", "Código inválido", parent=self.root)

class GestorVehiculos:
    def __init__(self, codigo_usuario, nombre_usuario):
        self.codigo_usuario = codigo_usuario
        self.root = ThemedTk(theme="arc")
        self.root.title(f"🚗 Gestor de Vehículos - {nombre_usuario}")
        self.root.geometry("1000x600")
        VentanaCentrada.centrar(self.root, 1000, 600)
        
        sv_ttk.set_theme("light")
        self.configurar_interfaz()
        self.actualizar_tabla()
        self.root.mainloop()
    
    def configurar_interfaz(self):
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('Arial', 11, 'bold'), foreground='#2c3e50')
        self.style.configure("Treeview", font=('Arial', 10), rowheight=30)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side="left", padx=5)
        self.buscador = ttk.Entry(search_frame, width=40)
        self.buscador.pack(side="left", padx=5)
        self.buscador.bind("<Return>", lambda event: self.realizar_busqueda())
        
        ttk.Button(
            search_frame,
            text="Buscar",
            command=self.realizar_busqueda,
            style="Accent.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            search_frame,
            text="Limpiar",
            command=self.limpiar_busqueda,
            style="Secondary.TButton"
        ).pack(side="left", padx=5)
        
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        self.tabla = ttk.Treeview(
            table_frame,
            columns=("id", "Nombre", "Ubicación", "Planta"),
            show="headings",
            selectmode="browse"
        )
        
        self.tabla.column("id", width=0, stretch=tk.NO)
        for col, ancho in [("Nombre", 400), ("Ubicación", 300), ("Planta", 150)]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tabla.bind("<Double-1>", lambda e: self.mostrar_detalles())
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        botones = [
            ("➕ Agregar", self.agregar_vehiculo),
            ("✏️ Editar", self.editar_vehiculo),
            ("🗑️ Eliminar", self.eliminar_vehiculo),
            ("🔄 Actualizar", self.actualizar_tabla)
        ]
        
        for texto, comando in botones:
            ttk.Button(
                btn_frame,
                text=texto,
                command=comando,
                style="Accent.TButton"
            ).pack(side="left", padx=10, ipadx=10)
    
    def realizar_busqueda(self):
        texto = self.buscador.get()
        resultados = obtener_datos(
            "SELECT id, nombre, ubicacion, planta FROM vehiculos "
            "WHERE (nombre LIKE %s OR ubicacion LIKE %s) "
            "AND codigo_usuario = %s",
            (f"%{texto}%", f"%{texto}%", self.codigo_usuario)
        )
        self.actualizar_tabla(resultados)
    
    def limpiar_busqueda(self):
        self.buscador.delete(0, tk.END)
        self.actualizar_tabla()
    
    def actualizar_tabla(self, datos=None):
        self.tabla.delete(*self.tabla.get_children())
        datos = datos or obtener_datos(
            "SELECT id, nombre, ubicacion, planta FROM vehiculos "
            "WHERE codigo_usuario = %s",
            (self.codigo_usuario,)
        )
        for item in datos:
            self.tabla.insert("", "end", values=item)
    
    def agregar_vehiculo(self):
        popup = tk.Toplevel()
        popup.title("➕ Nuevo Vehículo")
        popup.geometry("400x400")
        VentanaCentrada.centrar(popup, 400, 400)
        
        campos = [
            ("Nombre", "entry", ""),
            ("Ubicación", "entry", ""),
            ("Planta", "combo", (1, 2, 3, 4, 5)),
            ("Obtención", "combo", ("Comprado", "Obtenido")),
            ("Mejoras", "combo", ("Maximo HSW Armado", "Maximo Armado", "Maximo HSW", "Maximo", "Normal"))
        ]
        
        entries = []
        for campo in campos:
            ttk.Label(popup, text=campo[0]).pack(pady=5)
            if campo[1] == "combo":
                entry = ttk.Combobox(popup, values=campo[2])
                entry.set(campo[2][0])
            else:
                entry = ttk.Entry(popup)
                entry.insert(0, campo[2])
            entry.pack(pady=5, ipadx=20)
            entries.append(entry)
        
        def guardar():
            try:
                planta = int(entries[2].get())
                if not 1 <= planta <= 5:
                    raise ValueError
                
                ejecutar_consulta(
                    "INSERT INTO vehiculos (nombre, ubicacion, planta, obtencion, mejoras, codigo_usuario) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        entries[0].get(),
                        entries[1].get(),
                        planta,
                        entries[3].get(),
                        entries[4].get(),
                        self.codigo_usuario
                    )
                )
                self.actualizar_tabla()
                popup.destroy()
                messagebox.showinfo("Éxito", "Vehículo registrado", parent=self.root)
            except ValueError:
                messagebox.showerror("Error", "Planta inválida", parent=popup)
        
        ttk.Button(popup, text="Guardar", command=guardar, style="Accent.TButton").pack(pady=20)
    
    def editar_vehiculo(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un vehículo", parent=self.root)
            return
        
        id_vehiculo = self.tabla.item(seleccionado[0])["values"][0]
        datos = obtener_datos(
            "SELECT nombre, ubicacion, planta, obtencion, mejoras FROM vehiculos "
            "WHERE id = %s AND codigo_usuario = %s",
            (id_vehiculo, self.codigo_usuario)
        )
        
        popup = tk.Toplevel()
        popup.title("✏️ Editar Vehículo")
        popup.geometry("400x400")
        VentanaCentrada.centrar(popup, 400, 400)
        
        campos = [
            ("Nombre", "entry", datos[0][0]),
            ("Ubicación", "entry", datos[0][1]),
            ("Planta", "combo", (1, 2, 3, 4, 5), datos[0][2]),
            ("Obtención", "combo", ("Comprado", "Obtenido"), datos[0][3]),
            ("Mejoras", "combo", ("Maximo HSW Armado", "Maximo Armado", "Maximo HSW", "Maximo", "Normal"), datos[0][4])
        ]
        
        entries = []
        for campo in campos:
            ttk.Label(popup, text=campo[0]).pack(pady=5)
            if campo[1] == "combo":
                entry = ttk.Combobox(popup, values=campo[2])
                entry.set(campo[3])
            else:
                entry = ttk.Entry(popup)
                entry.insert(0, campo[2])
            entry.pack(pady=5, ipadx=20)
            entries.append(entry)
        
        def actualizar():
            try:
                planta = int(entries[2].get())
                if not 1 <= planta <= 5:
                    raise ValueError
                
                ejecutar_consulta(
                    "UPDATE vehiculos SET nombre=%s, ubicacion=%s, planta=%s, "
                    "obtencion=%s, mejoras=%s WHERE id=%s AND codigo_usuario=%s",
                    (
                        entries[0].get(),
                        entries[1].get(),
                        planta,
                        entries[3].get(),
                        entries[4].get(),
                        id_vehiculo,
                        self.codigo_usuario
                    )
                )
                self.actualizar_tabla()
                popup.destroy()
                messagebox.showinfo("Éxito", "Cambios guardados", parent=self.root)
            except ValueError:
                messagebox.showerror("Error", "Planta inválida", parent=popup)
        
        ttk.Button(popup, text="Actualizar", command=actualizar, style="Accent.TButton").pack(pady=20)
    
    def eliminar_vehiculo(self):
        seleccionado = self.tabla.selection()
        if seleccionado:
            id_vehiculo = self.tabla.item(seleccionado[0])["values"][0]
            if messagebox.askyesno(
                "Confirmar",
                "¿Eliminar este vehículo permanentemente?",
                icon="warning",
                parent=self.root
            ):
                ejecutar_consulta(
                    "DELETE FROM vehiculos WHERE id = %s AND codigo_usuario = %s",
                    (id_vehiculo, self.codigo_usuario)
                )
                self.actualizar_tabla()
    
    def mostrar_detalles(self):
        seleccionado = self.tabla.selection()
        if not seleccionado: return
        
        id_vehiculo = self.tabla.item(seleccionado[0])["values"][0]
        datos = obtener_datos(
            "SELECT nombre, ubicacion, planta, obtencion, mejoras FROM vehiculos "
            "WHERE id = %s AND codigo_usuario = %s",
            (id_vehiculo, self.codigo_usuario)
        )
        
        detalle_ventana = tk.Toplevel()
        detalle_ventana.title("Detalles completos")
        VentanaCentrada.centrar(detalle_ventana, 300, 250)
        
        info = [
            ("Nombre:", datos[0][0]),
            ("Ubicación:", datos[0][1]),
            ("Planta:", datos[0][2]),
            ("Obtención:", datos[0][3]),
            ("Mejoras:", datos[0][4])
        ]
        
        for texto, valor in info:
            frame = ttk.Frame(detalle_ventana)
            frame.pack(pady=3, fill="x", padx=20)
            ttk.Label(frame, text=texto, width=12, anchor="w").pack(side="left")
            ttk.Label(frame, text=valor).pack(side="left")
        
        ttk.Button(detalle_ventana, text="Cerrar", command=detalle_ventana.destroy).pack(pady=10)

if __name__ == "__main__":
    ejecutar_consulta("""
        CREATE TABLE IF NOT EXISTS usuarios (
            codigo VARCHAR(20) PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL
        )
    """)
    
    ejecutar_consulta("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            ubicacion VARCHAR(255) NOT NULL,
            planta INT NOT NULL CHECK (planta BETWEEN 1 AND 5),
            obtencion VARCHAR(20) NOT NULL,
            mejoras VARCHAR(20) NOT NULL,
            codigo_usuario VARCHAR(20) NOT NULL,
            FOREIGN KEY (codigo_usuario) REFERENCES usuarios(codigo)
        )
    """)
    
    LoginWindow()