import tkinter as tk
from clases.interfazModerna import ModernInterface


if __name__ == "__main__":
    app = ModernInterface()
    # Crear menú después de inicializar la interfaz
    app.crear_menu()
    
    # Atajos de teclado adicionales
    app.bind("<Control-n>", lambda e: app.nuevo_archivo())
    app.bind("<Delete>", lambda e: app.eliminar_fila())
    
    app.mainloop()