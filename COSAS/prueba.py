import pandas as pd
import tkinter as tk
from tkinter import ttk

# Simulación de datos para este ejemplo
datos = pd.DataFrame({
    'Sub ID': [1, 2, 3, 5, 6, 8],  # Ejemplo de Sub ID con errores en consecutividad
    'Value': [10, 15, 20, 25, 30, 35]
})

# Validación de Sub ID consecutivos
def validar_sub_id_consecutivos(datos):
    errores = []
    for i in range(1, len(datos)):
        if datos['Sub ID'].iloc[i] != datos['Sub ID'].iloc[i - 1] + 1:
            errores.append(i)  # Guardar el índice de la fila con el error
    return errores

# Función para resaltar las filas con errores
def resaltar_errores(tree, errores):
    for idx, item in enumerate(tree.get_children()):
        if idx in errores:
            tree.item(item, tags="error")
    tree.tag_configure("error", background="tomato", foreground="white")

# Crear la ventana principal
root = tk.Tk()
root.title("Validación de Sub ID")
root.geometry("700x500")
root.configure(bg="#f5f5f5")

# Variables para almacenar datos dinámicamente
errores_sub_id = validar_sub_id_consecutivos(datos)
num_filas = len(datos)
num_errores = len(errores_sub_id)

# Configurar estilos para ttk
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 11))
style.configure("TButton", font=("Arial", 11), padding=5)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
style.configure("Treeview", rowheight=25, font=("Arial", 10))

# Mostrar la cantidad de filas y errores
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, pady=10, padx=10)

ttk.Label(info_frame, text=f"Cantidad de filas: {num_filas}", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
ttk.Label(info_frame, text=f"Errores encontrados: {num_errores}", anchor="w").grid(row=0, column=1, sticky="w", padx=5)

# Mostrar la tabla completa
tabla_frame = ttk.Frame(root)
tabla_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree = ttk.Treeview(tabla_frame, columns=list(datos.columns), show="headings")
for col in datos.columns:
    tree.heading(col, text=col)
    tree.column(col, minwidth=0, width=150, anchor="center")

# Insertar los datos en el Treeview
for idx, row in datos.iterrows():
    tree.insert("", tk.END, values=row.tolist())

# Resaltar errores
resaltar_errores(tree, errores_sub_id)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Detalle de errores en un panel desplegable
detalle_frame = ttk.Frame(root)
detalle_frame.pack(fill=tk.X, padx=10, pady=10)

detalle_label = ttk.Label(detalle_frame, text="Detalle de fila seleccionada:")
detalle_label.pack(side=tk.TOP, anchor="w")

detalle_text = tk.Text(detalle_frame, height=5, wrap=tk.WORD, state="disabled", bg="#f0f0f0", font=("Arial", 10))
detalle_text.pack(fill=tk.X, expand=False)

# Mostrar detalles al seleccionar una fila
def mostrar_detalle(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        fila_idx = tree.index(selected_item)
        fila = datos.iloc[fila_idx]
        detalle_text.config(state="normal")
        detalle_text.delete(1.0, tk.END)
        detalle_text.insert(tk.END, f"Fila {fila_idx + 1}:\n{fila.to_string(index=True)}")
        detalle_text.config(state="disabled")

tree.bind("<<TreeviewSelect>>", mostrar_detalle)

# Botón para salir
boton_frame = ttk.Frame(root)
boton_frame.pack(fill=tk.X, pady=10, padx=10)

btn_salir = ttk.Button(boton_frame, text="Salir", command=root.destroy)
btn_salir.pack(side=tk.RIGHT)

# Iniciar la aplicación
root.mainloop()
