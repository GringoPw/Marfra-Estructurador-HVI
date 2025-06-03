import pandas as pd
import pyperclip

def verificar_correlatividad(sub_id_columna):
    """
    Verifica si los valores de 'sub_id' son correlativos.
    :param sub_id_columna: Columna 'sub_id' del DataFrame.
    :return: True si son correlativos, False si falta algún número.
    """
    # Verificar la secuencia de los 'sub_id'
    min_sub_id = sub_id_columna.min()
    max_sub_id = sub_id_columna.max()
    expected_rows = max_sub_id - min_sub_id + 1
    
    # Imprimir el mínimo, máximo y la cantidad de filas
    print(f"Min Sub ID: {min_sub_id}")
    print(f"Max Sub ID: {max_sub_id}")
    print(f"Cantidad de filas esperadas: {expected_rows}")
    print(f"Cantidad de filas reales: {len(sub_id_columna)}")

    # Verificar si la cantidad de filas es igual a las filas esperadas
    if len(sub_id_columna) != expected_rows:
        return False, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)
    
    # Verificar que todos los números entre min_sub_id y max_sub_id estén presentes
    missing_sub_ids = set(range(min_sub_id, max_sub_id + 1)) - set(sub_id_columna)
    if missing_sub_ids:
        return False, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)
    
    return True, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)

def copiar_al_portapapeles(datos):
    """
    Copia los datos a portapapeles para que se puedan pegar en Excel.
    Verifica que la columna 'sub_id' sea correlativa.
    
    :param datos: Lista de listas o DataFrame con los datos a copiar.
    """
    # Verificar si los datos son un DataFrame
    if isinstance(datos, pd.DataFrame):
        if 'Sub ID' in datos.columns:
            # En lugar de 'SubID', usa 'Sub ID'
            correlativo_valido, min_sub_id, max_sub_id, expected_rows, actual_rows = verificar_correlatividad(datos['Sub ID'])

            
            if not correlativo_valido:
                # Mostrar advertencia de error en la consola
                print(f"\033[91m¡Error! La columna 'sub_id' no es correlativa.\033[0m")
                print(f"\033[91mMin: {min_sub_id}, Max: {max_sub_id}, Filas esperadas: {expected_rows}, Filas reales: {actual_rows}\033[0m")
                return  # Salir sin copiar al portapapeles
            else:
                print(f"\033[92mVerificación exitosa: 'sub_id' es correlativa.\033[0m")
        else:
            # Advertencia si 'sub_id' no está en los datos
            print("\033[91m¡Error! La columna 'sub_id' no está presente en los datos.\033[0m")
            return  # Salir sin copiar al portapapeles
    
    # Convertir datos a un formato de texto adecuado
    if isinstance(datos, pd.DataFrame):
        datos_str = datos.to_csv(sep="\t", index=False, header=False)  # Usar tabulaciones para Excel
    else:
        datos_str = "\n".join(["\t".join(map(str, row)) for row in datos])  # Convertir lista a string

    # Copiar al portapapeles
    pyperclip.copy(datos_str)
    print("\033[92mDatos copiados al portapapaples.\033[0m")
