def filtrar_datos_limpios(ruta_archivo, parent=None, debug=False):
    """
    Elimina encabezados, estadísticas y líneas inválidas.
    Reconstruye líneas partidas y Sub ID divididos en dos columnas.
    
    Args:
        ruta_archivo: Ruta al archivo a procesar
        parent: Objeto padre para mostrar diálogos de error
        debug: Si es True, muestra mensajes de depuración
    """
    import re
    from errores import mostrar_error_procesamiento_linea

    patrones_sucios = [
        r"System Test Report",
        r"PREMIER ART R",
        r"\d{2}-\d{2}-\d{4}\d{2}:\d{2}[AP]M",
        r"Test ID",
        r"Test Type",
        r"Test Date",
        r"Remarks",
        r"COOP\.AGR",
        r"UHML.*ML.*UI.*Str.*Elg.*Mic",
        r"Test.*Sub ID.*\(mm\)",
        r"No.*\)",
        r"Statistics",
        r"Avg\d*-?\d*",
        r"Median",
        r"SD",
        r"CV%",
        r"Min",
        r"Max",
        r"MARFRA SA",
        r"Temp\(.*C\)",
        r"^\s*$",
        r"tifier.*MGTA.*LOTE"
    ]

    lineas_limpias = []
    buffer_linea = None

    try:
        with open(ruta_archivo, 'r', encoding='latin1') as archivo:
            lineas = archivo.readlines()

        for i, linea in enumerate(lineas):
            try:
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue

                if any(re.search(p, linea_limpia, re.IGNORECASE) for p in patrones_sucios):
                    if debug:
                        print(f"[Línea {i+1}] Eliminada por patrón: {linea_limpia}")
                    continue

                partes = linea_limpia.split()
                # 🔧 Caso especial: Más de 16 columnas - fusionar las dos primeras
                if len(partes) > 16:
                    partes[0] = partes[0] + partes[1]  # Fusionar las dos primeras columnas
                    partes.pop(1)  # Eliminar la segunda columna ahora fusionada
                    if debug:
                        print(f"[Línea {i+1}] 🔧 Fusionadas columnas 1 y 2 por exceso de columnas: {linea_limpia}")

                # 🔧 Sub ID partido tipo '00 049420'
                if len(partes) >= 2 and re.match(r'^\d{2}$', partes[0]) and re.match(r'^\d{6}$', partes[1]):
                    partes[0] = partes[0] + partes[1]  # unir Sub ID
                    partes.pop(1)
                    linea_limpia = " ".join(partes)
                    if debug:
                        print(f"[Línea {i+1}] 🔧 Sub ID corregido: {linea_limpia}")

                # Si es un Sub ID suelto
                if len(partes) == 1 and re.match(r'^\d{5,}$', partes[0]):
                    if buffer_linea:
                        buffer_partes = buffer_linea.split()
                        buffer_partes[0] = partes[0]
                        nueva_linea = " ".join(buffer_partes)
                        columnas = nueva_linea.split()
                        if 5 <= len(columnas) <= 16:
                            try:
                                float(columnas[0])
                                lineas_limpias.append(nueva_linea)
                                if debug:
                                    print(f"[Línea {i+1}] ✅ Reconstruida: {nueva_linea}")
                            except ValueError:
                                if debug:
                                    print(f"[Línea {i+1}] ❌ Sub ID inválido tras reconstrucción: {nueva_linea}")
                        else:
                            if debug:
                                print(f"[Línea {i+1}] ❌ Cols inválidas tras unir: {nueva_linea}")
                        buffer_linea = None
                    else:
                        if debug:
                            print(f"[Línea {i+1}] ⚠️ Sub ID suelto sin línea previa: {linea_limpia}")
                    continue

                if re.match(r'^\d{5,}$', partes[0]) and 5 <= len(partes) <= 16:
                    try:
                        float(partes[0])
                        lineas_limpias.append(" ".join(partes))
                        if debug:
                            print(f"[Línea {i+1}] ✅ Aceptada normal: {' '.join(partes)}")
                        buffer_linea = None
                    except ValueError:
                        buffer_linea = linea_limpia
                        if debug:
                            print(f"[Línea {i+1}] ❌ Sub ID inválido: {linea_limpia}")
                else:
                    if "-" in partes[0]:
                        buffer_linea = linea_limpia
                        if debug:
                            print(f"[Línea {i+1}] ⏳ Posible línea partida: {linea_limpia}")
                    else:
                        buffer_linea = None
                        try:
                            float(partes[0])
                            lineas_limpias.append(" ".join(partes))
                            if debug:
                                print(f"[Línea {i+1}] ✅ Aceptada (espaciada pero válida): {linea_limpia}")
                        except ValueError:
                            if debug:
                                print(f"[Línea {i+1}] ❌ No válida y sin guion: {linea_limpia}")
            except Exception as e:
                # Capturar errores específicos de procesamiento de línea
                error_msg = str(e)
                if debug:
                    print(f"[Línea {i+1}] ❌ Error de procesamiento: {error_msg}")
                
                # Mostrar el error en la interfaz si se proporcionó un objeto parent
                if parent:
                    mostrar_error_procesamiento_linea(parent, linea, i+1, error_msg)

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return []

    if debug:
        print(f"\n✅ Total líneas válidas: {len(lineas_limpias)}")
    return lineas_limpias