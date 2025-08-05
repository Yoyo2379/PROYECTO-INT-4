# Sistema de Abarrotes - Interfaz Gráfica

Una aplicación de escritorio desarrollada en Python con tkinter para gestionar un sistema de abarrotes con base de datos PostgreSQL.

## Características

- **Gestión de Productos**: Agregar, editar, eliminar y consultar productos
- **Sistema de Ventas**: Carrito de compras con procesamiento de ventas
- **Gestión de Usuarios**: Administración de usuarios con roles
- **Control de Stock**: Registro de entradas y alertas de stock bajo
- **Reportes**: Generación de reportes de ventas y productos

## Requisitos

- Python 3.7+
- PostgreSQL
- Dependencias de Python (ver requirements.txt)

## Instalación

1. Clona o descarga los archivos del proyecto
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura la base de datos en `config.json`:
   ```json
   {
       "database": {
           "host": "localhost",
           "database": "abarrotes",
           "user": "tu_usuario",
           "password": "tu_password",
           "port": 5432
       }
   }
   ```

4. Asegúrate de que la base de datos PostgreSQL esté ejecutándose y que la base de datos `abarrotes` esté creada con el esquema proporcionado.

## Uso

Ejecuta la aplicación:
```bash
python main.py
```

### Pestañas Disponibles

1. **Productos**: Gestión completa del inventario
2. **Ventas**: Procesamiento de ventas con carrito de compras
3. **Usuarios**: Administración de usuarios del sistema
4. **Control de Stock**: Registro de entradas y alertas
5. **Reportes**: Generación de reportes diversos

### Funcionalidades por Pestaña

#### Productos
- Agregar nuevos productos con todos sus datos
- Editar productos existentes
- Eliminar productos
- Visualizar lista completa de productos

#### Ventas
- Seleccionar usuario y método de pago
- Buscar productos disponibles
- Agregar productos al carrito
- Procesar venta (utiliza la función `registrar_venta` de la BD)

#### Usuarios
- Crear usuarios con roles (admin, vendedor, supervisor)
- Editar información de usuarios
- Gestión de contraseñas (hasheadas con SHA256)

#### Control de Stock
- Registrar entradas de mercancía
- Ver alertas de productos con stock bajo
- Actualización automática de inventario

#### Reportes
- Ventas por fecha
- Productos más vendidos
- Ventas por usuario
- Filtros por rango de fechas

## Estructura de Archivos

- `main.py`: Aplicación principal con interfaz gráfica
- `config.json`: Configuración de conexión a base de datos
- `requirements.txt`: Dependencias de Python
- `README.md`: Este archivo de documentación

## Notas Técnicas

- La aplicación utiliza la función `registrar_venta()` de PostgreSQL para procesar ventas
- Las contraseñas se almacenan hasheadas con SHA256
- La interfaz está optimizada para resoluciones de 1400x900 o superiores
- Manejo de errores con mensajes informativos al usuario

## Personalización

Puedes modificar fácilmente:
- Colores y estilos de la interfaz
- Campos adicionales en los formularios
- Nuevos tipos de reportes
- Validaciones personalizadas