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

# Función para validar que los cursos existan en la lista de referencia
def validar_cursos_existentes(oferta_df, lista_cursos_df):
    cursos_no_existentes = oferta_df[~oferta_df['CURSO'].isin(lista_cursos_df['CURSO'])]
    if not cursos_no_existentes.empty:
        return False, f"Los siguientes cursos no existen en la lista de referencia: {', '.join(cursos_no_existentes['CURSO'].unique())}"
    return True, "Todos los cursos existen en la lista de referencia."

# Función para validar el tamaño máximo de una columna de texto
def validar_tamano_columna(df, columna, tamano_maximo):
    if df[columna].str.len().max() > tamano_maximo:
        return False, f"La columna {columna} excede el tamaño máximo de {tamano_maximo} caracteres."
    return True, f"La columna {columna} cumple con el tamaño máximo de {tamano_maximo} caracteres."

# Función para validar el rango de una columna numérica (como créditos)
def validar_rango(df, columna, min_val, max_val):
    if df[columna].min() < min_val or df[columna].max() > max_val:
        return False, f"La columna {columna} tiene valores fuera del rango permitido ({min_val}-{max_val})."
    return True, f"Todos los valores de la columna {columna} están dentro del rango permitido."

# Función para validar que la hora de inicio sea menor que la hora de fin
def validar_horarios(df, inicio_col, fin_col):
    if (df[inicio_col] > df[fin_col]).any():
        return False, "Existen horarios donde la hora de inicio es mayor o igual que la hora de fin."
    return True, "Los horarios son válidos."

# Función para validar duplicados en una columna
def validar_duplicados(df, columna):
    duplicados = df[df.duplicated(subset=[columna], keep=False)]
    if not duplicados.empty:
        return False, f"Existen duplicados en la columna {columna}: {', '.join(duplicados[columna].unique())}"
    return True, f"No se encontraron duplicados en la columna {columna}."

# Título de la app
st.title("Validación de Oferta Académica")

# Subir archivo de oferta académica
archivo_oferta = st.file_uploader("Sube el archivo de oferta académica", type=["xlsx"])

# Subir archivo de lista de cursos
archivo_lista_cursos = st.file_uploader("Sube el archivo de lista de cursos", type=["xlsx"])

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

    # 2. Validar que los cursos existan en la lista de referencia
    total_validaciones += 1
    resultado, mensaje = validar_cursos_existentes(oferta_df, lista_cursos_df)
    resultado = mostrar_validacion(resultado, mensaje, "Algunos cursos no existen en la lista de referencia.")
    if resultado:
        validaciones_exitosas += 1

    # 3. Validar que el 'NOMBRE DE CURSO' no esté vacío
    total_validaciones += 1
    resultado, mensaje = validar_no_vacio(oferta_df, 'NOMBRE DE CURSO')
    resultado = mostrar_validacion(resultado, mensaje, "La columna 'NOMBRE DE CURSO' tiene valores vacíos.")
    if resultado:
        validaciones_exitosas += 1

    # 4. Validar que el nombre del curso no exceda los 100 caracteres
    total_validaciones += 1
    resultado, mensaje = validar_tamano_columna(oferta_df, 'NOMBRE DE CURSO', 100)
    resultado = mostrar_validacion(resultado, mensaje, "El nombre del curso excede los 100 caracteres.")
    if resultado:
        validaciones_exitosas += 1

    # 5. Validar el rango de créditos (por ejemplo, de 1 a 6 créditos)
    total_validaciones += 1
    resultado, mensaje = validar_rango(oferta_df, 'CREDITOS', 1, 6)
    resultado = mostrar_validacion(resultado, mensaje, "Los créditos están fuera del rango permitido.")
    if resultado:
        validaciones_exitosas += 1

    # 6. Validar los horarios de inicio y fin
    total_validaciones += 1
    resultado, mensaje = validar_horarios(oferta_df, 'HORA INICIO', 'HORA FIN')
    resultado = mostrar_validacion(resultado, mensaje, "Existen horarios incorrectos.")
    if resultado:
        validaciones_exitosas += 1

    # 7. Validar duplicados en la columna 'CURSO'
    total_validaciones += 1
    resultado, mensaje = validar_duplicados(oferta_df, 'CURSO')
    resultado = mostrar_validacion(resultado, mensaje, "Se encontraron duplicados en la columna 'CURSO'.")
    if resultado:
        validaciones_exitosas += 1

    # Calcular porcentaje de validaciones exitosas
    porcentaje_exitosas = (validaciones_exitosas / total_validaciones) * 100

    # Mostrar barra de progreso dinámica
    st.write("### Resumen de Validaciones")
    st.progress(porcentaje_exitosas / 100)

    # Mostrar estadísticas
    st.write(f"Validaciones exitosas: {validaciones_exitosas}/{total_validaciones}")
    st.write(f"Porcentaje de validaciones exitosas: {porcentaje_exitosas:.2f}%")
else:
    st.write("Por favor, sube ambos archivos para continuar.")
