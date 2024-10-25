import streamlit as st
import pandas as pd

# Función para mostrar validaciones con colores e íconos
def mostrar_validacion(resultado, mensaje_exito, mensaje_error):
    if resultado:
        st.success(f"✔️ {mensaje_exito}")
    else:
        st.error(f"❌ {mensaje_error}")
    return resultado

# Función para validar que una columna no esté vacía
def validar_no_vacio(df, columna):
    if df[columna].isnull().any():
        return False, f"La columna {columna} contiene valores vacíos."
    return True, f"La columna {columna} no tiene valores vacíos."

# Validación general para formato de fechas
def validar_fecha(df, columna):
    try:
        pd.to_datetime(df[columna], errors='raise')
        return True, f"La columna {columna} tiene fechas válidas."
    except:
        return False, f"La columna {columna} contiene fechas no válidas."

# Validación de DNI en formato numérico de 8 dígitos
def validar_dni(df, columna):
    if df[columna].astype(str).str.match(r'^\d{8}$').all():
        return True, f"La columna {columna} tiene DNIs válidos."
    return False, f"La columna {columna} contiene DNIs no válidos."

# Validación de valores específicos (como modalidades o días)
def validar_valores(df, columna, valores_permitidos):
    if df[columna].isin(valores_permitidos).all():
        return True, f"La columna {columna} tiene valores válidos."
    return False, f"La columna {columna} contiene valores no válidos."

# Validación de rango numérico para columnas específicas
def validar_rango(df, columna, min_val, max_val):
    if df[columna].between(min_val, max_val).all():
        return True, f"Todos los valores de la columna {columna} están dentro del rango permitido."
    return False, f"La columna {columna} tiene valores fuera del rango permitido ({min_val}-{max_val})."

# Validación para verificar duplicados
def validar_duplicados(df, columna):
    duplicados = df[df.duplicated(subset=[columna], keep=False)]
    if duplicados.empty:
        return True, f"No se encontraron duplicados en la columna {columna}."
    return False, f"Existen duplicados en la columna {columna}: {', '.join(duplicados[columna].unique())}"

# Función para validar horarios (hora de inicio < hora de fin)
def validar_horarios(df, inicio_col, fin_col):
    if (df[inicio_col] < df[fin_col]).all():
        return True, "Los horarios de inicio y fin son válidos."
    return False, "Existen horarios donde la hora de inicio es mayor o igual que la hora de fin."

# Título de la app
st.title("Validación de Oferta Académica")

# Subir archivo de oferta académica
archivo_oferta = st.file_uploader("Sube el archivo de oferta académica", type=["xlsx"])

# Subir archivo de lista de cursos
archivo_lista_cursos = st.file_uploader("Sube el archivo de lista de cursos", type=["xlsx"])

# Observaciones para los errores
observaciones = []

if archivo_oferta and archivo_lista_cursos:
    # Leer archivos
    oferta_df = pd.read_excel(archivo_oferta, sheet_name='oferta curso')
    lista_cursos_df = pd.read_excel(archivo_lista_cursos, sheet_name='Hoja1')

    # Lista para contar validaciones exitosas y fallidas
    total_validaciones = 0
    validaciones_exitosas = 0

    # Validaciones
    st.write("### Validaciones:")

    # 1. Validar que la columna 'CURSO' no esté vacía
    total_validaciones += 1
    resultado, mensaje = validar_no_vacio(oferta_df, 'CURSO')
    resultado = mostrar_validacion(resultado, mensaje, "La columna 'CURSO' tiene valores vacíos.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 2. Validar que los cursos existan en la lista de referencia
    total_validaciones += 1
    cursos_no_existentes = oferta_df[~oferta_df['CURSO'].isin(lista_cursos_df['CURSO'])]
    if cursos_no_existentes.empty:
        mensaje = "Todos los cursos existen en la lista de referencia."
        resultado = True
    else:
        mensaje = f"Los siguientes cursos no existen en la lista de referencia: {', '.join(cursos_no_existentes['CURSO'].unique())}"
        resultado = False
        observaciones.append(mensaje)
    mostrar_validacion(resultado, mensaje, mensaje)

    # 3. Validación del rango de créditos
    total_validaciones += 1
    resultado, mensaje = validar_rango(oferta_df, 'CREDITOS', 1, 6)
    resultado = mostrar_validacion(resultado, mensaje, "Los créditos están fuera del rango permitido.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 4. Validar que el DNI tenga 8 dígitos
    total_validaciones += 1
    resultado, mensaje = validar_dni(oferta_df, 'DNI DOCENTE')
    resultado = mostrar_validacion(resultado, mensaje, "DNI no válido en la columna 'DNI DOCENTE'.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 5. Validar que 'MODALIDAD' contenga valores permitidos
    modalidades_permitidas = ["Presencial", "Virtual", "Semipresencial"]
    total_validaciones += 1
    resultado, mensaje = validar_valores(oferta_df, 'MODALIDAD', modalidades_permitidas)
    resultado = mostrar_validacion(resultado, mensaje, "La columna 'MODALIDAD' contiene valores no válidos.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 6. Validar que 'FECHA INICIO CURSO' y 'FECHA FIN CURSO' sean válidas
    total_validaciones += 1
    resultado, mensaje = validar_fecha(oferta_df, 'FECHA INICIO CURSO')
    mostrar_validacion(resultado, mensaje, "Fecha no válida en 'FECHA INICIO CURSO'.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)
    
    total_validaciones += 1
    resultado, mensaje = validar_fecha(oferta_df, 'FECHA FIN CURSO')
    mostrar_validacion(resultado, mensaje, "Fecha no válida en 'FECHA FIN CURSO'.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 7. Validar los horarios de inicio y fin
    total_validaciones += 1
    resultado, mensaje = validar_horarios(oferta_df, 'HORA INICIO', 'HORA FIN')
    resultado = mostrar_validacion(resultado, mensaje, "Existen horarios incorrectos.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # 8. Validar duplicados en la columna 'CURSO'
    total_validaciones += 1
    resultado, mensaje = validar_duplicados(oferta_df, 'CURSO')
    resultado = mostrar_validacion(resultado, mensaje, "Se encontraron duplicados en la columna 'CURSO'.")
    if resultado:
        validaciones_exitosas += 1
    else:
        observaciones.append(mensaje)

    # Resumen y observaciones finales
    porcentaje_exitosas = (validaciones_exitosas / total_validaciones) * 100

    st.write("### Resumen de Validaciones")
    st.progress(porcentaje_exitosas / 100)
    st.write(f"Validaciones exitosas: {validaciones_exitosas}/{total_validaciones}")
    st.write(f"Porcentaje de validaciones exitosas: {porcentaje_exitosas:.2f}%")

    # Mostrar observaciones detalladas
    if observaciones:
        st.write("### Observaciones de Errores")
        for obs in observaciones:
            st.write(f"- {obs}")
else:
    st.write("Por favor, sube ambos archivos para continuar.")
