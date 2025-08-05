import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
import json
import hashlib

class AbarrotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Abarrotes")
        self.root.geometry("1400x900")
        
        # Cargar configuración
        self.load_config()
        
        # Variables para el carrito de ventas
        self.carrito = []
        self.total_venta = 0.0
        
        self.setup_ui()
        print("Aplicación iniciada correctamente!")  # Debug
        
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.db_config = config['database']
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")
            self.db_config = {
                'host': 'localhost',
                'database': 'abarrotes',
                'user': 'postgres',
                'password': 'password',
                'port': 5432
            }
        
    def setup_ui(self):
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.create_productos_tab()
        self.create_ventas_tab()
        self.create_usuarios_tab()
        self.create_stock_tab()
        self.create_reportes_tab()
        
    def get_connection(self):
        try:
            print(f"Intentando conectar con: {self.db_config}")  # Debug
            conn = psycopg2.connect(**self.db_config)
            print("Conexión exitosa!")  # Debug
            return conn
        except Exception as e:
            print(f"Error de conexión: {e}")  # Debug
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
            return None
    
    def create_productos_tab(self):
        # Frame principal para productos
        productos_frame = ttk.Frame(self.notebook)
        self.notebook.add(productos_frame, text="Productos")
        
        # Frame superior para formulario
        form_frame = ttk.LabelFrame(productos_frame, text="Gestión de Productos")
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.producto_nombre = ttk.Entry(form_frame, width=20)
        self.producto_nombre.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Descripción:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.producto_descripcion = ttk.Entry(form_frame, width=30)
        self.producto_descripcion.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Precio Venta:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.producto_precio_venta = ttk.Entry(form_frame, width=15)
        self.producto_precio_venta.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Precio Compra:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.producto_precio_compra = ttk.Entry(form_frame, width=15)
        self.producto_precio_compra.grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Stock Actual:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.producto_stock_actual = ttk.Entry(form_frame, width=10)
        self.producto_stock_actual.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Stock Mínimo:").grid(row=2, column=2, sticky='w', padx=5, pady=2)
        self.producto_stock_minimo = ttk.Entry(form_frame, width=10)
        self.producto_stock_minimo.grid(row=2, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Código Barras:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.producto_codigo_barras = ttk.Entry(form_frame, width=20)
        self.producto_codigo_barras.grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Fecha Caducidad:").grid(row=3, column=2, sticky='w', padx=5, pady=2)
        self.producto_fecha_caducidad = ttk.Entry(form_frame, width=15)
        self.producto_fecha_caducidad.grid(row=3, column=3, padx=5, pady=2)
        
        # Botones
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="Agregar", command=self.agregar_producto).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Actualizar", command=self.actualizar_producto).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Eliminar", command=self.eliminar_producto).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Limpiar", command=self.limpiar_producto_form).pack(side='left', padx=5)
        
        # Treeview para mostrar productos
        tree_frame = ttk.LabelFrame(productos_frame, text="Lista de Productos")
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')
        
        # Treeview
        self.productos_tree = ttk.Treeview(tree_frame, 
                                         columns=('ID', 'Nombre', 'Descripción', 'P.Venta', 'P.Compra', 'Stock', 'S.Min', 'Código', 'Caducidad'),
                                         show='headings',
                                         yscrollcommand=tree_scroll_y.set,
                                         xscrollcommand=tree_scroll_x.set)
        
        # Configurar scrollbars
        tree_scroll_y.config(command=self.productos_tree.yview)
        tree_scroll_x.config(command=self.productos_tree.xview)
        
        # Configurar columnas
        columns = ['ID', 'Nombre', 'Descripción', 'P.Venta', 'P.Compra', 'Stock', 'S.Min', 'Código', 'Caducidad']
        widths = [50, 150, 200, 80, 80, 60, 60, 120, 100]
        
        for col, width in zip(columns, widths):
            self.productos_tree.heading(col, text=col)
            self.productos_tree.column(col, width=width)
        
        self.productos_tree.pack(fill='both', expand=True)
        
        # Bind para selección
        self.productos_tree.bind('<<TreeviewSelect>>', self.on_producto_select)
        
        # Cargar productos al inicio
        self.cargar_productos()
    
    def agregar_producto(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Validar campos requeridos
            if not all([self.producto_nombre.get(), self.producto_precio_venta.get(), 
                       self.producto_precio_compra.get(), self.producto_stock_actual.get(),
                       self.producto_stock_minimo.get()]):
                messagebox.showerror("Error", "Todos los campos obligatorios deben estar llenos")
                return
            
            # Preparar fecha de caducidad
            fecha_caducidad = self.producto_fecha_caducidad.get() if self.producto_fecha_caducidad.get() else None
            
            cursor.execute("""
                INSERT INTO producto (nombre, descripcion, precio_venta, precio_compra, 
                                    stock_actual, stock_minimo, codigo_barras, fecha_caducidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.producto_nombre.get(),
                self.producto_descripcion.get(),
                float(self.producto_precio_venta.get()),
                float(self.producto_precio_compra.get()),
                int(self.producto_stock_actual.get()),
                int(self.producto_stock_minimo.get()),
                self.producto_codigo_barras.get() if self.producto_codigo_barras.get() else None,
                fecha_caducidad
            ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            self.limpiar_producto_form()
            self.cargar_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {e}")
        finally:
            if conn:
                conn.close()
    
    def actualizar_producto(self):
        selected = self.productos_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para actualizar")
            return
            
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            item = self.productos_tree.item(selected[0])
            producto_id = item['values'][0]
            
            fecha_caducidad = self.producto_fecha_caducidad.get() if self.producto_fecha_caducidad.get() else None
            
            cursor.execute("""
                UPDATE producto SET nombre=%s, descripcion=%s, precio_venta=%s, precio_compra=%s,
                                  stock_actual=%s, stock_minimo=%s, codigo_barras=%s, fecha_caducidad=%s
                WHERE id_producto=%s
            """, (
                self.producto_nombre.get(),
                self.producto_descripcion.get(),
                float(self.producto_precio_venta.get()),
                float(self.producto_precio_compra.get()),
                int(self.producto_stock_actual.get()),
                int(self.producto_stock_minimo.get()),
                self.producto_codigo_barras.get() if self.producto_codigo_barras.get() else None,
                fecha_caducidad,
                producto_id
            ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            self.limpiar_producto_form()
            self.cargar_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {e}")
        finally:
            if conn:
                conn.close()
    
    def eliminar_producto(self):
        selected = self.productos_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            try:
                conn = self.get_connection()
                if not conn:
                    return
                    
                cursor = conn.cursor()
                
                item = self.productos_tree.item(selected[0])
                producto_id = item['values'][0]
                
                cursor.execute("DELETE FROM producto WHERE id_producto=%s", (producto_id,))
                conn.commit()
                
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.limpiar_producto_form()
                self.cargar_productos()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {e}")
            finally:
                if conn:
                    conn.close()
    
    def cargar_productos(self):
        print("Cargando productos...")  # Debug
        try:
            conn = self.get_connection()
            if not conn:
                print("No se pudo obtener conexión")  # Debug
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM producto ORDER BY nombre")
            productos = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.productos_tree.get_children():
                self.productos_tree.delete(item)
            
            # Insertar productos
            for producto in productos:
                self.productos_tree.insert('', 'end', values=producto)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if conn:
                conn.close()
    
    def on_producto_select(self, event):
        selected = self.productos_tree.selection()
        if selected:
            item = self.productos_tree.item(selected[0])
            values = item['values']
            
            # Llenar formulario con datos seleccionados
            self.producto_nombre.delete(0, 'end')
            self.producto_nombre.insert(0, values[1])
            
            self.producto_descripcion.delete(0, 'end')
            self.producto_descripcion.insert(0, values[2] if values[2] else '')
            
            self.producto_precio_venta.delete(0, 'end')
            self.producto_precio_venta.insert(0, values[3])
            
            self.producto_precio_compra.delete(0, 'end')
            self.producto_precio_compra.insert(0, values[4])
            
            self.producto_stock_actual.delete(0, 'end')
            self.producto_stock_actual.insert(0, values[5])
            
            self.producto_stock_minimo.delete(0, 'end')
            self.producto_stock_minimo.insert(0, values[6])
            
            self.producto_codigo_barras.delete(0, 'end')
            self.producto_codigo_barras.insert(0, values[7] if values[7] else '')
            
            self.producto_fecha_caducidad.delete(0, 'end')
            self.producto_fecha_caducidad.insert(0, values[8] if values[8] else '')
    
    def limpiar_producto_form(self):
        self.producto_nombre.delete(0, 'end')
        self.producto_descripcion.delete(0, 'end')
        self.producto_precio_venta.delete(0, 'end')
        self.producto_precio_compra.delete(0, 'end')
        self.producto_stock_actual.delete(0, 'end')
        self.producto_stock_minimo.delete(0, 'end')
        self.producto_codigo_barras.delete(0, 'end')
        self.producto_fecha_caducidad.delete(0, 'end')
    
    def create_ventas_tab(self):
        # Frame principal para ventas
        ventas_frame = ttk.Frame(self.notebook)
        self.notebook.add(ventas_frame, text="Ventas")
        
        # Frame izquierdo para nueva venta
        left_frame = ttk.LabelFrame(ventas_frame, text="Nueva Venta")
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Selección de usuario
        ttk.Label(left_frame, text="Usuario:").pack(anchor='w', padx=5, pady=2)
        self.venta_usuario = ttk.Combobox(left_frame, state='readonly')
        self.venta_usuario.pack(fill='x', padx=5, pady=2)
        
        # Método de pago
        ttk.Label(left_frame, text="Método de Pago:").pack(anchor='w', padx=5, pady=2)
        self.venta_metodo_pago = ttk.Combobox(left_frame, values=['efectivo', 'tarjeta', 'vale'], state='readonly')
        self.venta_metodo_pago.pack(fill='x', padx=5, pady=2)
        
        # Búsqueda de productos
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar Producto:").pack(anchor='w')
        self.producto_search = ttk.Entry(search_frame)
        self.producto_search.pack(fill='x', pady=2)
        self.producto_search.bind('<KeyRelease>', self.buscar_productos)
        
        # Lista de productos disponibles
        ttk.Label(left_frame, text="Productos Disponibles:").pack(anchor='w', padx=5, pady=(10,2))
        
        productos_list_frame = ttk.Frame(left_frame)
        productos_list_frame.pack(fill='both', expand=True, padx=5, pady=2)
        
        productos_scroll = ttk.Scrollbar(productos_list_frame)
        productos_scroll.pack(side='right', fill='y')
        
        self.productos_listbox = tk.Listbox(productos_list_frame, yscrollcommand=productos_scroll.set)
        self.productos_listbox.pack(fill='both', expand=True)
        productos_scroll.config(command=self.productos_listbox.yview)
        
        # Cantidad y botón agregar
        add_frame = ttk.Frame(left_frame)
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="Cantidad:").pack(side='left')
        self.cantidad_entry = ttk.Entry(add_frame, width=10)
        self.cantidad_entry.pack(side='left', padx=5)
        
        ttk.Button(add_frame, text="Agregar al Carrito", command=self.agregar_al_carrito).pack(side='left', padx=5)
        
        # Frame derecho para carrito
        right_frame = ttk.LabelFrame(ventas_frame, text="Carrito de Compras")
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para carrito
        carrito_scroll = ttk.Scrollbar(right_frame)
        carrito_scroll.pack(side='right', fill='y')
        
        self.carrito_tree = ttk.Treeview(right_frame,
                                       columns=('Producto', 'Cantidad', 'Precio', 'Subtotal'),
                                       show='headings',
                                       yscrollcommand=carrito_scroll.set)
        
        carrito_scroll.config(command=self.carrito_tree.yview)
        
        # Configurar columnas del carrito
        self.carrito_tree.heading('Producto', text='Producto')
        self.carrito_tree.heading('Cantidad', text='Cantidad')
        self.carrito_tree.heading('Precio', text='Precio')
        self.carrito_tree.heading('Subtotal', text='Subtotal')
        
        self.carrito_tree.column('Producto', width=200)
        self.carrito_tree.column('Cantidad', width=80)
        self.carrito_tree.column('Precio', width=80)
        self.carrito_tree.column('Subtotal', width=80)
        
        self.carrito_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Total y botones
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill='x', padx=5, pady=5)
        
        self.total_label = ttk.Label(total_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(anchor='e')
        
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Quitar Item", command=self.quitar_del_carrito).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Limpiar Carrito", command=self.limpiar_carrito).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Procesar Venta", command=self.procesar_venta).pack(side='right', padx=5)
        
        # Cargar datos iniciales
        self.cargar_usuarios_venta()
        self.cargar_productos_venta()
    
    def cargar_usuarios_venta(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, nombre FROM usuario ORDER BY nombre")
            usuarios = cursor.fetchall()
            
            self.venta_usuario['values'] = [f"{u[0]} - {u[1]}" for u in usuarios]
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
        finally:
            if conn:
                conn.close()
    
    def cargar_productos_venta(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, nombre, precio_venta, stock_actual FROM producto WHERE stock_actual > 0 ORDER BY nombre")
            self.productos_disponibles = cursor.fetchall()
            
            self.productos_listbox.delete(0, 'end')
            for producto in self.productos_disponibles:
                self.productos_listbox.insert('end', f"{producto[1]} - ${producto[2]} (Stock: {producto[3]})")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if conn:
                conn.close()
    
    def buscar_productos(self, event):
        search_term = self.producto_search.get().lower()
        self.productos_listbox.delete(0, 'end')
        
        for producto in self.productos_disponibles:
            if search_term in producto[1].lower():
                self.productos_listbox.insert('end', f"{producto[1]} - ${producto[2]} (Stock: {producto[3]})")
    
    def agregar_al_carrito(self):
        selected = self.productos_listbox.curselection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
            
        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida")
            return
        
        # Obtener producto seleccionado
        index = selected[0]
        if self.producto_search.get():
            # Si hay búsqueda, encontrar el producto correcto
            search_term = self.producto_search.get().lower()
            filtered_products = [p for p in self.productos_disponibles if search_term in p[1].lower()]
            if index < len(filtered_products):
                producto = filtered_products[index]
            else:
                return
        else:
            producto = self.productos_disponibles[index]
        
        # Verificar stock
        if cantidad > producto[3]:
            messagebox.showerror("Error", f"Stock insuficiente. Disponible: {producto[3]}")
            return
        
        # Agregar al carrito
        subtotal = cantidad * float(producto[2])
        item_carrito = {
            'id_producto': producto[0],
            'nombre': producto[1],
            'cantidad': cantidad,
            'precio_unitario': float(producto[2]),
            'subtotal': subtotal
        }
        
        self.carrito.append(item_carrito)
        self.actualizar_carrito_display()
        self.cantidad_entry.delete(0, 'end')
    
    def actualizar_carrito_display(self):
        # Limpiar carrito display
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        # Agregar items
        self.total_venta = 0
        for item in self.carrito:
            self.carrito_tree.insert('', 'end', values=(
                item['nombre'],
                item['cantidad'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            self.total_venta += item['subtotal']
        
        self.total_label.config(text=f"Total: ${self.total_venta:.2f}")
    
    def quitar_del_carrito(self):
        selected = self.carrito_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un item del carrito")
            return
        
        # Obtener índice del item seleccionado
        item_index = self.carrito_tree.index(selected[0])
        del self.carrito[item_index]
        self.actualizar_carrito_display()
    
    def limpiar_carrito(self):
        self.carrito.clear()
        self.actualizar_carrito_display()
    
    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
            
        if not self.venta_usuario.get():
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
            
        if not self.venta_metodo_pago.get():
            messagebox.showwarning("Advertencia", "Seleccione un método de pago")
            return
        
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Obtener ID del usuario
            usuario_id = int(self.venta_usuario.get().split(' - ')[0])
            
            # Preparar productos para la función
            productos_json = json.dumps([{
                'id_producto': item['id_producto'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario']
            } for item in self.carrito])
            
            # Llamar a la función de la base de datos
            cursor.execute("SELECT registrar_venta(%s, %s, %s)", 
                         (usuario_id, self.venta_metodo_pago.get(), productos_json))
            
            conn.commit()
            
            messagebox.showinfo("Éxito", f"Venta procesada correctamente\nTotal: ${self.total_venta:.2f}")
            
            # Limpiar formulario
            self.limpiar_carrito()
            self.venta_usuario.set('')
            self.venta_metodo_pago.set('')
            self.cargar_productos_venta()  # Actualizar stock
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar venta: {e}")
        finally:
            if conn:
                conn.close()
    
    def create_usuarios_tab(self):
        # Frame principal para usuarios
        usuarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(usuarios_frame, text="Usuarios")
        
        # Frame superior para formulario
        form_frame = ttk.LabelFrame(usuarios_frame, text="Gestión de Usuarios")
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.usuario_nombre = ttk.Entry(form_frame, width=25)
        self.usuario_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.usuario_usuario = ttk.Entry(form_frame, width=20)
        self.usuario_usuario.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.usuario_password = ttk.Entry(form_frame, width=20, show='*')
        self.usuario_password.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Rol:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.usuario_rol = ttk.Combobox(form_frame, values=['admin', 'vendedor', 'supervisor'], state='readonly')
        self.usuario_rol.grid(row=1, column=3, padx=5, pady=5)
        
        # Botones
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="Agregar", command=self.agregar_usuario).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Actualizar", command=self.actualizar_usuario).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Eliminar", command=self.eliminar_usuario).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Limpiar", command=self.limpiar_usuario_form).pack(side='left', padx=5)
        
        # Treeview para mostrar usuarios
        tree_frame = ttk.LabelFrame(usuarios_frame, text="Lista de Usuarios")
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')
        
        # Treeview
        self.usuarios_tree = ttk.Treeview(tree_frame,
                                        columns=('ID', 'Nombre', 'Usuario', 'Rol'),
                                        show='headings',
                                        yscrollcommand=tree_scroll.set)
        
        tree_scroll.config(command=self.usuarios_tree.yview)
        
        # Configurar columnas
        self.usuarios_tree.heading('ID', text='ID')
        self.usuarios_tree.heading('Nombre', text='Nombre')
        self.usuarios_tree.heading('Usuario', text='Usuario')
        self.usuarios_tree.heading('Rol', text='Rol')
        
        self.usuarios_tree.column('ID', width=50)
        self.usuarios_tree.column('Nombre', width=200)
        self.usuarios_tree.column('Usuario', width=150)
        self.usuarios_tree.column('Rol', width=100)
        
        self.usuarios_tree.pack(fill='both', expand=True)
        
        # Bind para selección
        self.usuarios_tree.bind('<<TreeviewSelect>>', self.on_usuario_select)
        
        # Cargar usuarios al inicio
        self.cargar_usuarios()
    
    def agregar_usuario(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Validar campos requeridos
            if not all([self.usuario_nombre.get(), self.usuario_usuario.get(), 
                       self.usuario_password.get(), self.usuario_rol.get()]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Hash de la contraseña
            password_hash = hashlib.sha256(self.usuario_password.get().encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO usuario (nombre, usuario, contraseña_hash, rol)
                VALUES (%s, %s, %s, %s)
            """, (
                self.usuario_nombre.get(),
                self.usuario_usuario.get(),
                password_hash,
                self.usuario_rol.get()
            ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario agregado correctamente")
            self.limpiar_usuario_form()
            self.cargar_usuarios()
            
        except psycopg2.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar usuario: {e}")
        finally:
            if conn:
                conn.close()
    
    def actualizar_usuario(self):
        selected = self.usuarios_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para actualizar")
            return
            
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            item = self.usuarios_tree.item(selected[0])
            usuario_id = item['values'][0]
            
            # Si hay contraseña nueva, hashearla
            if self.usuario_password.get():
                password_hash = hashlib.sha256(self.usuario_password.get().encode()).hexdigest()
                cursor.execute("""
                    UPDATE usuario SET nombre=%s, usuario=%s, contraseña_hash=%s, rol=%s
                    WHERE id_usuario=%s
                """, (
                    self.usuario_nombre.get(),
                    self.usuario_usuario.get(),
                    password_hash,
                    self.usuario_rol.get(),
                    usuario_id
                ))
            else:
                cursor.execute("""
                    UPDATE usuario SET nombre=%s, usuario=%s, rol=%s
                    WHERE id_usuario=%s
                """, (
                    self.usuario_nombre.get(),
                    self.usuario_usuario.get(),
                    self.usuario_rol.get(),
                    usuario_id
                ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            self.limpiar_usuario_form()
            self.cargar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar usuario: {e}")
        finally:
            if conn:
                conn.close()
    
    def eliminar_usuario(self):
        selected = self.usuarios_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este usuario?"):
            try:
                conn = self.get_connection()
                if not conn:
                    return
                    
                cursor = conn.cursor()
                
                item = self.usuarios_tree.item(selected[0])
                usuario_id = item['values'][0]
                
                cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (usuario_id,))
                conn.commit()
                
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.limpiar_usuario_form()
                self.cargar_usuarios()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
            finally:
                if conn:
                    conn.close()
    
    def cargar_usuarios(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, nombre, usuario, rol FROM usuario ORDER BY nombre")
            usuarios = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.usuarios_tree.get_children():
                self.usuarios_tree.delete(item)
            
            # Insertar usuarios
            for usuario in usuarios:
                self.usuarios_tree.insert('', 'end', values=usuario)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
        finally:
            if conn:
                conn.close()
    
    def on_usuario_select(self, event):
        selected = self.usuarios_tree.selection()
        if selected:
            item = self.usuarios_tree.item(selected[0])
            values = item['values']
            
            # Llenar formulario con datos seleccionados
            self.usuario_nombre.delete(0, 'end')
            self.usuario_nombre.insert(0, values[1])
            
            self.usuario_usuario.delete(0, 'end')
            self.usuario_usuario.insert(0, values[2])
            
            self.usuario_rol.set(values[3])
            
            # Limpiar campo de contraseña
            self.usuario_password.delete(0, 'end')
    
    def limpiar_usuario_form(self):
        self.usuario_nombre.delete(0, 'end')
        self.usuario_usuario.delete(0, 'end')
        self.usuario_password.delete(0, 'end')
        self.usuario_rol.set('')  
        
    def create_stock_tab(self):
        # Frame principal para stock
        stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(stock_frame, text="Control de Stock")
        
        # Frame superior para entrada de stock
        entrada_frame = ttk.LabelFrame(stock_frame, text="Entrada de Stock")
        entrada_frame.pack(fill='x', padx=10, pady=5)
        
        # Campos del formulario
        ttk.Label(entrada_frame, text="Producto:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.stock_producto = ttk.Combobox(entrada_frame, state='readonly', width=30)
        self.stock_producto.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Cantidad:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.stock_cantidad = ttk.Entry(entrada_frame, width=15)
        self.stock_cantidad.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Proveedor:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.stock_proveedor = ttk.Entry(entrada_frame, width=25)
        self.stock_proveedor.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Documento:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.stock_documento = ttk.Entry(entrada_frame, width=20)
        self.stock_documento.grid(row=1, column=3, padx=5, pady=5)
        
        # Botones
        buttons_frame = ttk.Frame(entrada_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="Registrar Entrada", command=self.registrar_entrada_stock).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Limpiar", command=self.limpiar_stock_form).pack(side='left', padx=5)
        
        # Frame para alertas de stock bajo
        alertas_frame = ttk.LabelFrame(stock_frame, text="Alertas de Stock Bajo")
        alertas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview para alertas
        alertas_scroll = ttk.Scrollbar(alertas_frame)
        alertas_scroll.pack(side='right', fill='y')
        
        self.alertas_tree = ttk.Treeview(alertas_frame,
                                       columns=('Producto', 'Stock Actual', 'Stock Mínimo', 'Diferencia'),
                                       show='headings',
                                       yscrollcommand=alertas_scroll.set)
        
        alertas_scroll.config(command=self.alertas_tree.yview)
        
        # Configurar columnas
        self.alertas_tree.heading('Producto', text='Producto')
        self.alertas_tree.heading('Stock Actual', text='Stock Actual')
        self.alertas_tree.heading('Stock Mínimo', text='Stock Mínimo')
        self.alertas_tree.heading('Diferencia', text='Diferencia')
        
        self.alertas_tree.column('Producto', width=250)
        self.alertas_tree.column('Stock Actual', width=100)
        self.alertas_tree.column('Stock Mínimo', width=100)
        self.alertas_tree.column('Diferencia', width=100)
        
        self.alertas_tree.pack(fill='both', expand=True)
        
        # Cargar datos iniciales
        self.cargar_productos_stock()
        self.cargar_alertas_stock()
    
    def cargar_productos_stock(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, nombre FROM producto ORDER BY nombre")
            productos = cursor.fetchall()
            
            self.stock_producto['values'] = [f"{p[0]} - {p[1]}" for p in productos]
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if conn:
                conn.close()
    
    def registrar_entrada_stock(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Validar campos requeridos
            if not all([self.stock_producto.get(), self.stock_cantidad.get(), self.stock_proveedor.get()]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios")
                return
            
            # Obtener ID del producto
            producto_id = int(self.stock_producto.get().split(' - ')[0])
            cantidad = int(self.stock_cantidad.get())
            
            # Registrar entrada
            cursor.execute("""
                INSERT INTO entrada_stock (id_producto, fecha_entrada, cantidad, proveedor, documento_referencia)
                VALUES (%s, CURRENT_DATE, %s, %s, %s)
            """, (
                producto_id,
                cantidad,
                self.stock_proveedor.get(),
                self.stock_documento.get() if self.stock_documento.get() else None
            ))
            
            # Actualizar stock del producto
            cursor.execute("""
                UPDATE producto SET stock_actual = stock_actual + %s WHERE id_producto = %s
            """, (cantidad, producto_id))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Entrada de stock registrada correctamente")
            self.limpiar_stock_form()
            self.cargar_alertas_stock()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar entrada: {e}")
        finally:
            if conn:
                conn.close()
    
    def cargar_alertas_stock(self):
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre, stock_actual, stock_minimo, (stock_actual - stock_minimo) as diferencia
                FROM producto 
                WHERE stock_actual <= stock_minimo
                ORDER BY diferencia ASC
            """)
            alertas = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.alertas_tree.get_children():
                self.alertas_tree.delete(item)
            
            # Insertar alertas
            for alerta in alertas:
                self.alertas_tree.insert('', 'end', values=alerta)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar alertas: {e}")
        finally:
            if conn:
                conn.close()
    
    def limpiar_stock_form(self):
        self.stock_producto.set('')
        self.stock_cantidad.delete(0, 'end')
        self.stock_proveedor.delete(0, 'end')
        self.stock_documento.delete(0, 'end')
    
    def create_reportes_tab(self):
        # Frame principal para reportes
        reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(reportes_frame, text="Reportes")
        
        # Frame superior para filtros
        filtros_frame = ttk.LabelFrame(reportes_frame, text="Filtros de Reporte")
        filtros_frame.pack(fill='x', padx=10, pady=5)
        
        # Tipo de reporte
        ttk.Label(filtros_frame, text="Tipo de Reporte:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.tipo_reporte = ttk.Combobox(filtros_frame, 
                                       values=['Ventas por Fecha', 'Productos Más Vendidos', 'Ventas por Usuario'],
                                       state='readonly')
        self.tipo_reporte.grid(row=0, column=1, padx=5, pady=5)
        
        # Fechas
        ttk.Label(filtros_frame, text="Fecha Inicio:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.fecha_inicio = ttk.Entry(filtros_frame, width=12)
        self.fecha_inicio.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filtros_frame, text="Fecha Fin:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.fecha_fin = ttk.Entry(filtros_frame, width=12)
        self.fecha_fin.grid(row=1, column=1, padx=5, pady=5)
        
        # Botón generar reporte
        ttk.Button(filtros_frame, text="Generar Reporte", command=self.generar_reporte).grid(row=1, column=2, padx=5, pady=5)
        
        # Frame para mostrar reporte
        reporte_frame = ttk.LabelFrame(reportes_frame, text="Resultado del Reporte")
        reporte_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview para reporte
        reporte_scroll = ttk.Scrollbar(reporte_frame)
        reporte_scroll.pack(side='right', fill='y')
        
        self.reporte_tree = ttk.Treeview(reporte_frame, yscrollcommand=reporte_scroll.set)
        reporte_scroll.config(command=self.reporte_tree.yview)
        self.reporte_tree.pack(fill='both', expand=True)
        
        # Label para totales
        self.total_reporte_label = ttk.Label(reporte_frame, text="", font=('Arial', 10, 'bold'))
        self.total_reporte_label.pack(anchor='e', padx=10, pady=5)
    
    def generar_reporte(self):
        if not self.tipo_reporte.get():
            messagebox.showwarning("Advertencia", "Seleccione un tipo de reporte")
            return
        
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Limpiar treeview anterior
            for item in self.reporte_tree.get_children():
                self.reporte_tree.delete(item)
            
            if self.tipo_reporte.get() == "Ventas por Fecha":
                self.generar_reporte_ventas_fecha(cursor)
            elif self.tipo_reporte.get() == "Productos Más Vendidos":
                self.generar_reporte_productos_vendidos(cursor)
            elif self.tipo_reporte.get() == "Ventas por Usuario":
                self.generar_reporte_ventas_usuario(cursor)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
        finally:
            if conn:
                conn.close()
    
    def generar_reporte_ventas_fecha(self, cursor):
        # Configurar columnas
        self.reporte_tree['columns'] = ('Fecha', 'ID Venta', 'Usuario', 'Total', 'Método Pago')
        self.reporte_tree['show'] = 'headings'
        
        for col in self.reporte_tree['columns']:
            self.reporte_tree.heading(col, text=col)
            self.reporte_tree.column(col, width=120)
        
        # Query
        where_clause = ""
        params = []
        
        if self.fecha_inicio.get():
            where_clause += " AND DATE(v.fecha_hora) >= %s"
            params.append(self.fecha_inicio.get())
        
        if self.fecha_fin.get():
            where_clause += " AND DATE(v.fecha_hora) <= %s"
            params.append(self.fecha_fin.get())
        
        query = f"""
            SELECT DATE(v.fecha_hora), v.id_venta, u.nombre, v.total, v.metodo_pago
            FROM venta v
            JOIN usuario u ON v.id_usuario = u.id_usuario
            WHERE 1=1 {where_clause}
            ORDER BY v.fecha_hora DESC
        """
        
        cursor.execute(query, params)
        ventas = cursor.fetchall()
        
        total_general = 0
        for venta in ventas:
            self.reporte_tree.insert('', 'end', values=venta)
            total_general += float(venta[3])
        
        self.total_reporte_label.config(text=f"Total General: ${total_general:.2f}")
    
    def generar_reporte_productos_vendidos(self, cursor):
        # Configurar columnas
        self.reporte_tree['columns'] = ('Producto', 'Cantidad Vendida', 'Total Vendido')
        self.reporte_tree['show'] = 'headings'
        
        for col in self.reporte_tree['columns']:
            self.reporte_tree.heading(col, text=col)
            self.reporte_tree.column(col, width=150)
        
        # Query
        where_clause = ""
        params = []
        
        if self.fecha_inicio.get():
            where_clause += " AND DATE(v.fecha_hora) >= %s"
            params.append(self.fecha_inicio.get())
        
        if self.fecha_fin.get():
            where_clause += " AND DATE(v.fecha_hora) <= %s"
            params.append(self.fecha_fin.get())
        
        query = f"""
            SELECT p.nombre, SUM(dv.cantidad), SUM(dv.subtotal)
            FROM detalle_venta dv
            JOIN producto p ON dv.id_producto = p.id_producto
            JOIN venta v ON dv.id_venta = v.id_venta
            WHERE 1=1 {where_clause}
            GROUP BY p.nombre
            ORDER BY SUM(dv.cantidad) DESC
        """
        
        cursor.execute(query, params)
        productos = cursor.fetchall()
        
        for producto in productos:
            self.reporte_tree.insert('', 'end', values=(
                producto[0], 
                producto[1], 
                f"${float(producto[2]):.2f}"
            ))
    
    def generar_reporte_ventas_usuario(self, cursor):
        # Configurar columnas
        self.reporte_tree['columns'] = ('Usuario', 'Cantidad Ventas', 'Total Vendido')
        self.reporte_tree['show'] = 'headings'
        
        for col in self.reporte_tree['columns']:
            self.reporte_tree.heading(col, text=col)
            self.reporte_tree.column(col, width=150)
        
        # Query
        where_clause = ""
        params = []
        
        if self.fecha_inicio.get():
            where_clause += " AND DATE(v.fecha_hora) >= %s"
            params.append(self.fecha_inicio.get())
        
        if self.fecha_fin.get():
            where_clause += " AND DATE(v.fecha_hora) <= %s"
            params.append(self.fecha_fin.get())
        
        query = f"""
            SELECT u.nombre, COUNT(v.id_venta), SUM(v.total)
            FROM venta v
            JOIN usuario u ON v.id_usuario = u.id_usuario
            WHERE 1=1 {where_clause}
            GROUP BY u.nombre
            ORDER BY SUM(v.total) DESC
        """
        
        cursor.execute(query, params)
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            self.reporte_tree.insert('', 'end', values=(
                usuario[0], 
                usuario[1], 
                f"${float(usuario[2]):.2f}"
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = AbarrotesApp(root)
    root.mainloop()