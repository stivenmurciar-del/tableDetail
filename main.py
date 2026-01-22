import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc
import os
import json

class SQLSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Estructura SQL Server")
        self.main_structure = None  # Estructura cargada o extraída
        self.create_widgets()

    def create_widgets(self):
        # Frame de conexión principal
        frame_main = ttk.LabelFrame(self.root, text="Base de Datos Principal")
        frame_main.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.main_conn_vars = self.create_conn_fields(frame_main)

        # Frame de conexión cliente
        frame_client = ttk.LabelFrame(self.root, text="Base de Datos Cliente")
        frame_client.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.client_conn_vars = self.create_conn_fields(frame_client)

        # Botones
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=2, column=0, pady=10)
        ttk.Button(btn_frame, text="Guardar estructura principal", command=self.save_main_structure).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cargar estructura principal", command=self.load_main_structure).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Comparar con cliente", command=self.compare_with_loaded_structure).grid(row=0, column=2, padx=5)
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.grid(row=3, column=0, pady=5)

    def create_conn_fields(self, parent):
        vars = {}
        ttk.Label(parent, text="Servidor:").grid(row=0, column=0, sticky="e")
        vars['server'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars['server'], width=25).grid(row=0, column=1)
        ttk.Label(parent, text="Base de Datos:").grid(row=1, column=0, sticky="e")
        vars['database'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars['database'], width=25).grid(row=1, column=1)
        ttk.Label(parent, text="Usuario:").grid(row=2, column=0, sticky="e")
        vars['user'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars['user'], width=25).grid(row=2, column=1)
        ttk.Label(parent, text="Contraseña:").grid(row=3, column=0, sticky="e")
        vars['password'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars['password'], show="*", width=25).grid(row=3, column=1)
        return vars

    def get_connection(self, conn_vars):
        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={conn_vars['server'].get()};DATABASE={conn_vars['database'].get()};UID={conn_vars['user'].get()};PWD={conn_vars['password'].get()}"
            )
            return conn
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))
            return None

    def extract_structure(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.name AS table_name, c.name AS column_name, c.column_id, ty.name AS data_type, c.max_length, c.is_nullable
            FROM sys.tables t
            JOIN sys.columns c ON t.object_id = c.object_id
            JOIN sys.types ty ON c.user_type_id = ty.user_type_id
            ORDER BY t.name, c.column_id
        """)
        structure = {}
        for row in cursor.fetchall():
            table = row.table_name
            if table not in structure:
                structure[table] = []
            structure[table].append({
                'column_name': row.column_name,
                'data_type': row.data_type,
                'max_length': row.max_length,
                'is_nullable': row.is_nullable
            })
        return structure


    def save_main_structure(self):
        self.status_label.config(text="Extrayendo estructura principal...")
        self.root.update()
        main_conn = self.get_connection(self.main_conn_vars)
        if not main_conn:
            self.status_label.config(text="Error de conexión a principal.")
            return
        try:
            main_struct = self.extract_structure(main_conn)
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(main_struct, f, indent=2)
                messagebox.showinfo("Éxito", f"Estructura guardada en: {file_path}")
                self.status_label.config(text="Estructura principal guardada.")
            else:
                self.status_label.config(text="Guardado cancelado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Error al guardar estructura.")
        finally:
            main_conn.close()

    def load_main_structure(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.main_structure = json.load(f)
                messagebox.showinfo("Éxito", f"Estructura principal cargada de: {file_path}")
                self.status_label.config(text="Estructura principal cargada.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="Error al cargar estructura.")
        else:
            self.status_label.config(text="Carga cancelada.")

    def compare_with_loaded_structure(self):
        if not self.main_structure:
            messagebox.showwarning("Advertencia", "Primero debes cargar una estructura principal.")
            self.status_label.config(text="Carga una estructura principal.")
            return
        self.status_label.config(text="Comparando con cliente...")
        self.root.update()
        client_conn = self.get_connection(self.client_conn_vars)
        if not client_conn:
            self.status_label.config(text="Error de conexión a cliente.")
            return
        try:
            client_struct = self.extract_structure(client_conn)
            sql_script = self.generate_sync_script(self.main_structure, client_struct)
            if sql_script:
                file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(sql_script)
                    messagebox.showinfo("Éxito", f"Script generado en: {file_path}")
                    self.status_label.config(text="Script generado correctamente.")
                else:
                    self.status_label.config(text="Guardado cancelado.")
            else:
                messagebox.showinfo("Sin cambios", "No se encontraron diferencias de estructura.")
                self.status_label.config(text="No hay diferencias.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Error al comparar.")
        finally:
            client_conn.close()

    def generate_sync_script(self, main_struct, client_struct):
        script = ""
        # Crear tablas que no existen en cliente
        for table in main_struct:
            if table not in client_struct:
                script += self.create_table_sql(table, main_struct[table]) + "\n"
        # Agregar columnas faltantes
        for table in main_struct:
            if table in client_struct:
                client_cols = {col['column_name']: col for col in client_struct[table]}
                for col in main_struct[table]:
                    if col['column_name'] not in client_cols:
                        script += self.add_column_sql(table, col) + "\n"
        return script

    def create_table_sql(self, table, columns):
        cols_sql = []
        for col in columns:
            cols_sql.append(self.column_def_sql(col))
        return f"CREATE TABLE [{table}] (\n    {',\n    '.join(cols_sql)}\n);"

    def add_column_sql(self, table, col):
        return f"ALTER TABLE [{table}] ADD {self.column_def_sql(col)};"

    def column_def_sql(self, col):
        type_str = col['data_type']
        if col['data_type'] in ['varchar', 'nvarchar', 'char', 'nchar']:
            type_str += f"({col['max_length'] if col['max_length'] > 0 else 'MAX'})"
        null_str = "NULL" if col['is_nullable'] else "NOT NULL"
        return f"[{col['column_name']}] {type_str} {null_str}"

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLSyncApp(root)
    root.mainloop()
