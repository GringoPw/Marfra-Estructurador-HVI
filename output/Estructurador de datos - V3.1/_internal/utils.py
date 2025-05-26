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
 
def promediar(datos, treeview):
    # Inicializamos las sumas y el conteo para el promedio
    suma_uhml = suma_ui = suma_str = suma_mic = suma_sfi = 0
    conteo = len(datos)

    # Sumar los valores de las columnas UHML, UI, STR y MIC
    for fila in datos:
        try:
            suma_uhml += float(fila[3])  # Columna 2 para UHML
            suma_ui += float(fila[5])  # Columna 3 para UI
            suma_str += float(fila[6])  # Columna 4 para STR
            suma_mic += float(fila[8])  # Columna 5 para MIC
            suma_sfi += float(fila[17])  # Columna 15 para SFI
        except ValueError:
            print(f"Advertencia: los datos no son numéricos en la fila {fila}")
            continue  # Omite esta fila y sigue con las demás

    # Calcular los promedios y redondearlos a 1 decimal
    if conteo > 0:
        promedio_uhml = round(suma_uhml / conteo, 1)
        promedio_ui = round(suma_ui / conteo, 1)
        promedio_str = round(suma_str / conteo, 1)
        promedio_mic = round(suma_mic / conteo, 1)
        promedio_sfi = round(suma_sfi / conteo, 1)
    else:
        promedio_uhml = promedio_ui = promedio_str = promedio_mic = promedio_sfi = (
            0  # Valor predeterminado en caso de no haber datos
        )

    # Umbral de diferencia aceptable
    umbral = 4

    # Actualizar los valores en el dataframe y resaltar en rojo si fueron modificados
    for i in range(conteo):
        fila = datos[i]

        # Verificar si los valores están fuera del umbral y modificarlos
        if abs(float(fila[3]) - promedio_uhml) > umbral:  # Columna 2 para UHML
            fila[3] = promedio_uhml
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_uhml", background="red")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_uhml",)
            )

        if abs(float(fila[5]) - promedio_ui) > umbral:  # Columna 4 para UI
            fila[5] = promedio_ui
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_ui", background="orange")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_ui",)
            )

        if abs(float(fila[6]) - promedio_str) > umbral:  # Columna 5 para STR
            fila[6] = promedio_str
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_str", background="yellow")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_str",)
            )

        if abs(float(fila[8]) - promedio_mic) > umbral:  # Columna 6 para MIC
            fila[8] = promedio_mic
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_mic", background="green")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_mic",)
            )

        if abs(float(fila[17]) - promedio_sfi) > umbral:  # Columna 16 para MIC
            fila[17] = promedio_sfi
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_sfi", background="lightblue")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_sfi",)
            )
