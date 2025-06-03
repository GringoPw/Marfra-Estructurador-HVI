# Importo el modulo de dialogos de error que esta en la carpeta "class"
# y lo renombro como errorDialog para evitar conflictos de nombres
from clases.errorDialogClass import ErrorDialog

def mostrar_error_lectura_archivo(parent, file_path, error_message, line_number=None):
    """Mostrar error específico de lectura de archivo"""
    error_data = {
        'message': error_message,
        'file_path': file_path,
    }
    if line_number:
        error_data['line_number'] = line_number
        
    dialog = ErrorDialog(parent, "Error de Lectura", "file_read", error_data)
    return dialog.show_and_wait()

def mostrar_error_validacion(parent, total_errors, error_types=None, error_list=None):
    """Mostrar error de validación con detalles"""
    error_data = {
        'total_errors': total_errors,
        'error_types': error_types or {},
        'error_list': error_list or []
    }
    
    dialog = ErrorDialog(parent, "Errores de Validación", "validation", error_data)
    return dialog.show_and_wait()

def mostrar_error_procesamiento(parent, operation, progress=0, technical_error=None):
    """Mostrar error de procesamiento"""
    error_data = {
        'operation': operation,
        'progress': progress
    }
    if technical_error:
        error_data['technical_error'] = technical_error
        
    dialog = ErrorDialog(parent, "Error de Procesamiento", "processing", error_data)
    return dialog.show_and_wait()

def mostrar_error_red(parent, connection_status="Desconectado", server_url=None):
    """Mostrar error de red/conexión"""
    error_data = {
        'connection_status': connection_status
    }
    if server_url:
        error_data['server_url'] = server_url
        
    dialog = ErrorDialog(parent, "Error de Conexión", "network", error_data)
    return dialog.show_and_wait()

def mostrar_error_general(parent, title, message):
    """Mostrar error general"""
    error_data = {'message': message}
    dialog = ErrorDialog(parent, title, "general", error_data)
    return dialog.show_and_wait()

def mostrar_error_procesamiento_linea(parent, linea, numero_linea, error_message):
    """Mostrar error específico de procesamiento de línea"""
    error_data = {
        'message': f"Error al procesar línea: {error_message}",
        'line_number': numero_linea,
        'line_content': linea
    }
    dialog = ErrorDialog(parent, "Error de Procesamiento", "general", error_data)
    return dialog.show_and_wait()