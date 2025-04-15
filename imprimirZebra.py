import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import zebra
import json

class EtiquetasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Impresión de Etiquetas Zebra ZD220")
        
        # Base de datos de productos
        self.productos = []
        
        # Configurar interfaz
        self.setup_ui()
        
    def setup_ui(self):
        # Marco para ingresar productos
        frame_ingreso = tk.LabelFrame(self.root, text="Ingresar Producto", padx=10, pady=10)
        frame_ingreso.pack(padx=10, pady=10, fill="x")
        
        # Campos del formulario
        tk.Label(frame_ingreso, text="Nombre del Producto:").grid(row=0, column=0, sticky="e")
        self.nombre_entry = tk.Entry(frame_ingreso, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_ingreso, text="Código de Barras:").grid(row=1, column=0, sticky="e")
        self.codigo_entry = tk.Entry(frame_ingreso, width=40)
        self.codigo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botones de ingreso
        btn_frame = tk.Frame(frame_ingreso)
        btn_frame.grid(row=2, column=1, pady=10, sticky="e")
        
        btn_agregar = tk.Button(btn_frame, text="Agregar Producto", command=self.agregar_producto)
        btn_agregar.pack(side="left", padx=5)
        
        btn_cargar = tk.Button(btn_frame, text="Cargar JSON", command=self.cargar_json)
        btn_cargar.pack(side="left", padx=5)
        
        # Lista de productos
        frame_lista = tk.LabelFrame(self.root, text="Productos Registrados", padx=10, pady=10)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(frame_lista, columns=("Nombre", "Código"), show="headings")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Código", text="Código de Barras")
        self.tree.pack(fill="both", expand=True)
        
        # Botones de acción
        frame_acciones = tk.Frame(self.root)
        frame_acciones.pack(padx=10, pady=10, fill="x")
        
        btn_imprimir = tk.Button(frame_acciones, text="Imprimir Etiquetas", command=self.imprimir_etiquetas)
        btn_imprimir.pack(side="right", padx=5)
        
        btn_eliminar = tk.Button(frame_acciones, text="Eliminar Seleccionado", command=self.eliminar_producto)
        btn_eliminar.pack(side="right", padx=5)
    
    def agregar_producto(self):
        nombre = self.nombre_entry.get()
        codigo = self.codigo_entry.get()
        
        if not nombre or not codigo:
            messagebox.showerror("Error", "Nombre y código de barras son obligatorios")
            return
        
        # Validar que el código sea numérico
        if not codigo.isdigit():
            messagebox.showerror("Error", "El código de barras debe contener solo números")
            return
        
        # Agregar a la lista
        self.productos.append({
            "nombre": nombre,
            "codigo": codigo
        })
        
        # Actualizar treeview
        self.tree.insert("", "end", values=(nombre, codigo))
        
        # Limpiar campos
        self.nombre_entry.delete(0, tk.END)
        self.codigo_entry.delete(0, tk.END)
        
        messagebox.showinfo("Éxito", "Producto agregado correctamente")
    
    def cargar_json(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                nuevos_productos = json.load(f)
                
                # Validar estructura del JSON
                if not isinstance(nuevos_productos, list):
                    raise ValueError("El archivo JSON debe contener un array de productos")
                
                for producto in nuevos_productos:
                    if not all(key in producto for key in ['nombre', 'codigo']):
                        raise ValueError("Cada producto debe tener 'nombre' y 'codigo'")
                    
                    if not str(producto['codigo']).isdigit():
                        raise ValueError("El código de barras debe contener solo números")
                
                # Limpiar lista actual
                self.productos.clear()
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Agregar nuevos productos
                for producto in nuevos_productos:
                    self.productos.append({
                        "nombre": producto["nombre"],
                        "codigo": str(producto["codigo"])
                    })
                    self.tree.insert("", "end", values=(producto["nombre"], producto["codigo"]))
                
                messagebox.showinfo("Éxito", f"{len(nuevos_productos)} productos cargados correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo JSON: {str(e)}")
    
    def eliminar_producto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        # Obtener índice
        index = self.tree.index(selected_item[0])
        
        # Eliminar de la lista y del treeview
        del self.productos[index]
        self.tree.delete(selected_item)
    
    def imprimir_etiquetas(self):
        if not self.productos:
            messagebox.showwarning("Advertencia", "No hay productos para imprimir")
            return
        
        try:
            # Conectar con la impresora Zebra
            printer = zebra.Zebra()
            printers = printer.getqueues()
            
            if not printers:
                messagebox.showerror("Error", "No se encontraron impresoras Zebra")
                return
                
            printer.setqueue(printers[0])  # Seleccionar la primera impresora Zebra encontrada
            
            # Generar etiquetas para cada producto
            for producto in self.productos:
                zpl_code = self.generar_zpl(producto)
                printer.output(zpl_code)
            
            messagebox.showinfo("Éxito", "Etiquetas enviadas a impresión")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al imprimir: {str(e)}")
    
    def generar_zpl(self, producto):
        # Plantilla ZPL para etiqueta (ajustable según necesidades)
        zpl_template = """^XA
        ^FO20,20^A0N,30,30^FD{nombre}^FS
        ^FO20,60^BY2^BCN,100,Y,N,N^FD{codigo}^FS
        ^XZ"""
        
        return zpl_template.format(
            nombre=producto["nombre"],
            codigo=producto["codigo"]
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = EtiquetasApp(root)
    root.mainloop()