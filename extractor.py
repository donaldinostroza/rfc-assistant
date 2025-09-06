import os
import requests
import sqlite3
from datetime import datetime, timedelta

# --- Configuración ---
# El nombre del archivo de la base de datos.
DB_FILE = "licitaciones.db"

def get_api_ticket():
    """
    Recupera el API Ticket desde las variables de entorno (GitHub Secrets).
    Lanza un error si la variable no está configurada.
    """
    ticket = os.environ.get('API_TICKET')
    if not ticket:
        # Este error detendrá la ejecución si el secret no está configurado en GitHub.
        raise ValueError("La variable de entorno API_TICKET no está configurada. "
                         "Asegúrate de añadirla en los Secrets de tu repositorio.")
    return ticket

def setup_database():
    """
    Asegura que el archivo de la base de datos y las tablas existan.
    La función sqlite3.connect() crea el archivo .db si este no existe.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the rfcs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rfcs (
            codigo_externo TEXT PRIMARY KEY,
            nombre TEXT,
            estado INTEGER,
            fecha_cierre TEXT
        )
    ''')
    
    # Create the purchase_orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            estado INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_FILE}' asegurada y lista.")

def fetch_rfcs_from_date(date_str, api_ticket):
    """Obtiene las RFCs (licitaciones) de una fecha específica desde la API."""
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha={date_str}&ticket={api_ticket}"
    try:
        response = requests.get(url, timeout=30)  # Añadido un timeout
        response.raise_for_status()  # Lanza un error para respuestas HTTP 4xx/5xx
        return response.json().get('Listado', [])
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Mercado Público: {e}")
        return []

def save_rfcs(rfcs_list):
    """Guarda una lista de RFCs en la base de datos, evitando duplicados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    new_rfcs_count = 0
    
    for rfc in rfcs_list:
        try:
            # 'INSERT OR IGNORE' es una forma eficiente de manejar duplicados
            # basados en la PRIMARY KEY (codigo_externo).
            cursor.execute('''
                INSERT OR IGNORE INTO rfcs (codigo_externo, nombre, estado, fecha_cierre)
                VALUES (?, ?, ?, ?)
            ''', (
                rfc.get('CodigoExterno'),
                rfc.get('Nombre'),
                int(rfc.get('CodigoEstado')) if rfc.get('CodigoEstado') is not None else None,
                rfc.get('FechaCierre')
            ))
            # cursor.rowcount será 1 si se insertó una nueva fila, 0 si se ignoró.
            if cursor.rowcount > 0:
                new_rfcs_count += 1
        except sqlite3.Error as e:
            print(f"Error al insertar RFC en la base de datos: {e}")

    conn.commit()
    conn.close()
    return new_rfcs_count

def fetch_purchase_orders_from_date(date_str, api_ticket):
    """Obtiene las órdenes de compra de una fecha específica desde la API."""
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha={date_str}&ticket={api_ticket}"
    try:
        response = requests.get(url, timeout=30)  # Añadido un timeout
        response.raise_for_status()  # Lanza un error para respuestas HTTP 4xx/5xx
        return response.json().get('Listado', [])
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de Órdenes de Compra: {e}")
        return []

def save_purchase_orders(purchase_orders_list):
    """Guarda una lista de órdenes de compra en la base de datos, evitando duplicados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    new_orders_count = 0
    
    for order in purchase_orders_list:
        try:
            # 'INSERT OR IGNORE' es una forma eficiente de manejar duplicados
            # basados en la PRIMARY KEY (codigo).
            cursor.execute('''
                INSERT OR IGNORE INTO purchase_orders (codigo, nombre, estado)
                VALUES (?, ?, ?)
            ''', (
                order.get('Codigo'),
                order.get('Nombre'),
                int(order.get('CodigoEstado')) if order.get('CodigoEstado') is not None else None
            ))
            # cursor.rowcount será 1 si se insertó una nueva fila, 0 si se ignoró.
            if cursor.rowcount > 0:
                new_orders_count += 1
        except sqlite3.Error as e:
            print(f"Error al insertar orden de compra en la base de datos: {e}")

    conn.commit()
    conn.close()
    return new_orders_count

if __name__ == "__main__":
    print("Iniciando proceso de extracción de RFCs y Órdenes de Compra...")
    
    try:
        # 1. Recupera el ticket de forma segura.
        api_ticket = get_api_ticket()
        
        # 2. Asegura que la BD y las tablas existan antes de cualquier operación.
        #    Este paso maneja el caso de la primera ejecución.
        setup_database()
        
        # 3. Calcula la fecha a consultar (día anterior).
        yesterday = datetime.now() - timedelta(days=1)
        date_to_fetch = yesterday.strftime('%d%m%Y')
        print(f"Buscando datos para la fecha: {date_to_fetch}")

        # 4. Obtiene las licitaciones (RFCs) desde la API.
        print("Extrayendo RFCs...")
        rfcs_list = fetch_rfcs_from_date(date_to_fetch, api_ticket)
        
        # 5. Obtiene las órdenes de compra desde la API.
        print("Extrayendo órdenes de compra...")
        purchase_orders_list = fetch_purchase_orders_from_date(date_to_fetch, api_ticket)
        
        # 6. Procesa y guarda los resultados de RFCs.
        rfcs_count = 0
        if rfcs_list:
            rfcs_count = save_rfcs(rfcs_list)
            print(f"Se agregaron {rfcs_count} nuevas RFCs.")
        else:
            print("No se encontraron RFCs para la fecha especificada o hubo un error de conexión.")
        
        # 7. Procesa y guarda los resultados de órdenes de compra.
        orders_count = 0
        if purchase_orders_list:
            orders_count = save_purchase_orders(purchase_orders_list)
            print(f"Se agregaron {orders_count} nuevas órdenes de compra.")
        else:
            print("No se encontraron órdenes de compra para la fecha especificada o hubo un error de conexión.")
            
        print(f"Proceso finalizado. Total: {rfcs_count} RFCs y {orders_count} órdenes de compra agregadas.")
            
    except ValueError as e:
        # Captura el error específico de la falta del API_TICKET.
        print(f"Error de Configuración: {e}")
    except Exception as e:
        # Captura cualquier otro error inesperado durante la ejecución.
        print(f"Ocurrió un error inesperado: {e}")