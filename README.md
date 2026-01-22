# Sincronizador de Estructura SQL Server

Esta aplicación permite comparar y sincronizar la estructura de tablas y columnas entre dos bases de datos SQL Server, generando archivos .sql con los scripts necesarios para igualar la estructura del cliente a la principal.

## Características
- Conexión a dos bases de datos SQL Server (principal y cliente)
- Extracción de estructura de tablas y columnas
- Comparación de estructuras
- Generación de scripts SQL para igualar la estructura del cliente
- Interfaz gráfica sencilla (Tkinter)

## Uso
1. Ingresa los datos de conexión para ambas bases de datos.
2. Extrae la estructura de la base principal.
3. Compara con la base del cliente.
4. Genera el archivo .sql con los cambios necesarios.

## Requisitos
- Python 3.8+
- Paquetes: `pyodbc`, `tkinter`

## Instalación de dependencias

```
py -m pip install -r requirements.txt
```

Tkinter suele venir incluido con Python. Si no lo tienes, instálalo según tu sistema operativo.

---

Este proyecto es solo para fines de sincronización de estructura (tablas y columnas). No modifica datos ni otros objetos (índices, procedimientos, etc.).