import streamlit as st
import pandas as pd
import re

# Función para normalizar nombres de columnas (eliminar espacios adicionales, saltos de línea y convertir a mayúsculas)
def normalizar_columnas(df):
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip().str.upper()
    return df

# Función para verificar la existencia de una columna y obtener su nombre real en el DataFrame
def obtener_columna(df, nombre_base):
    nombre_base = re.sub(r'\s+', ' ', nombre_base.strip().upper())
    for col in df.columns:
        col_normalizado = re.sub(r'\s+', ' ', col.strip().upper())
        if col_normalizado == nombre_base:
            return col
    return None

# Función para mostrar validación con observaciones detalladas
def mostrar_validacion(resultado, mensaje_exito, mensaje_error, detalles=None):
    if resultado:
        st.success(f"✔️ {mensaje_exito}")
    else:
        error_msg = f"❌ {mensaje_error}"
        if detalles:
            error_msg += f": {', '.join(map(str, detalles))}"
        st.error(error_msg)
        return mensaje_error if not detalles else f"{mensaje_error}: {', '.join(map(str, detalles))}"
    return None

# Validaciones individuales
def validar_no_vacio(df, columna):
    vacios = df[df[columna].isnull()]
    if vacios.empty:
        return True, f"La columna '{columna}' no tiene valores vacíos.", None
    return False, f"La columna '{columna}' contiene valores vacíos", vacios.index.tolist()

def validar_longitud(df, columna, longitud_max):
    largos = df[df[columna].str.len() > longitud_max]
    if largos.empty:
        return True, f"La columna '{columna}' cumple con el tamaño máximo de {longitud_max} caracteres.", None
    return False, f"El nombre del curso excede los {longitud_max} caracteres", largos.index.tolist()

def validar_rango(df, columna, min_val, max_val):
    fuera_rango = df[~df[columna].between(min_val, max_val)]
    if fuera_rango.empty:
        return True, f"Todos los valores de la columna '{columna}' están dentro del rango permitido (1-6).", None
    return False, f"La columna '{columna}' tiene valores fuera del rango permitido (1-6)", fuera_rango.index.tolist()

def validar_valores(df, columna, valores_permitidos):
    valores_invalidos = df[~df[columna].isin(valores_permitidos)]
    if valores_invalidos.empty:
        return True, f"La columna '{columna}' tiene valores válidos.", None
    return False, f"La columna '{columna}' contiene valores no válidos", valores_invalidos.index.tolist()

def validar_fecha(df, columna):
    fechas_invalidas = df[~pd.to_datetime(df[columna], errors='coerce').notnull()]
    if fechas_invalidas.empty:
        return True, f"La columna '{columna}' tiene fechas válidas.", None
    return False, f"La columna '{columna}' contiene fechas no válidas", fechas_invalidas.index.tolist()

def validar_dni(df, columna):
    # Valida tanto vacíos como formato de 8 dígitos
    vacios = df[df[columna].isnull()]
    if not vacios.empty:
        return False, f"La columna '{columna}' contiene valores vacíos", vacios.index.tolist()
    dni_invalidos = df[~df[columna].astype(str).str.match(r'^\d{8}$')]
    if dni_invalidos.empty:
        return True, f"La columna '{columna}' tiene DNIs válidos.", None
    return False, f"La columna '{columna}' contiene DNIs no válidos", dni_invalidos.index.tolist()

def validar_horarios(df, inicio_col, fin_col):
    horarios_invalidos = df[df[inicio_col] >= df[fin_col]]
    if horarios_invalidos.empty:
        return True, "Los horarios de inicio y fin son válidos.", None
    return False, "Existen horarios donde la hora de inicio es mayor o igual que la hora de fin", horarios_invalidos.index.tolist()

# Título de la app
st.title("Validación de Oferta Académica")

# Subir archivo de oferta académica y lista de cursos
archivo_oferta = st.file_uploader("Sube el archivo de oferta académica", type=["xlsx"])
archivo_lista_cursos = st.file_uploader("Sube el archivo de lista de cursos", type=["xlsx"])

# Observaciones para los errores
observaciones = []

if archivo_oferta and archivo_lista_cursos:
    # Leer y normalizar columnas
    oferta_df = normalizar_columnas(pd.read_excel(archivo_oferta, sheet_name='oferta curso'))
    lista_cursos_df = normalizar_columnas(pd.read_excel(archivo_lista_cursos, sheet_name='Hoja1'))

    # Lista para contar validaciones exitosas y fallidas
    total_validaciones = 0
    validaciones_exitosas = 0

    # Validaciones
    st.write("### Validaciones:")

    # Validación de que la columna CURSO no esté vacía y los cursos existan en la lista de referencia
    columna_curso = obtener_columna(oferta_df, 'CURSO')
    if columna_curso:
        total_validaciones += 1
        resultado, mensaje, detalles = validar_no_vacio(oferta_df, columna_curso)
        observacion = mostrar_validacion(resultado, "La columna 'CURSO' no tiene valores vacíos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)
        
        # Validación de que los cursos existan en la lista de referencia (sin considerar vacíos)
        if 'CURSO' in lista_cursos_df.columns:
            cursos_no_existentes = oferta_df[oferta_df[columna_curso].notnull() & ~oferta_df[columna_curso].isin(lista_cursos_df['CURSO'])]
            if cursos_no_existentes.empty:
                mensaje = "Todos los cursos existen en la lista de referencia."
                resultado = True
            else:
                mensaje = "Los siguientes cursos no existen en la lista de referencia"
                resultado = False
                observacion = mostrar_validacion(resultado, mensaje, mensaje, cursos_no_existentes[columna_curso].unique().tolist())
                observaciones.append(observacion)

    # Validación de que la columna NOMBRE DE CURSO no esté vacía
    columna_nombre_curso = obtener_columna(oferta_df, 'NOMBRE DE CURSO')
    if columna_nombre_curso:
        total_validaciones += 1
        resultado, mensaje, detalles = validar_no_vacio(oferta_df, columna_nombre_curso)
        observacion = mostrar_validacion(resultado, "La columna 'NOMBRE DE CURSO' no tiene valores vacíos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

        # Validación de longitud máxima del NOMBRE DE CURSO
        total_validaciones += 1
        resultado, mensaje, detalles = validar_longitud(oferta_df, columna_nombre_curso, 100)
        observacion = mostrar_validacion(resultado, "La columna 'NOMBRE DE CURSO' cumple con el tamaño máximo de 100 caracteres.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

    # Validación del rango de créditos
    columna_creditos = obtener_columna(oferta_df, 'CREDITOS')
    if columna_creditos:
        total_validaciones += 1
        resultado, mensaje, detalles = validar_rango(oferta_df, columna_creditos, 1, 6)
        observacion = mostrar_validacion(resultado, "Todos los valores de la columna 'CREDITOS' están dentro del rango permitido.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

    # Validación del formato de DNI DOCENTE
    columna_dni = obtener_columna(oferta_df, 'DNI DOCENTE')
    if columna_dni:
        total_validaciones += 1
        resultado, mensaje, detalles = validar_dni(oferta_df, columna_dni)
        observacion = mostrar_validacion(resultado, "La columna 'DNI DOCENTE' tiene DNIs válidos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

    # Validación de valores en la columna MODALIDAD (vacíos y contenido válido)
    columna_modalidad = obtener_columna(oferta_df, 'MODALIDAD')
    if columna_modalidad:
        total_validaciones += 1
        # Validar que no esté vacía
        resultado, mensaje, detalles = validar_no_vacio(oferta_df, columna_modalidad)
        observacion = mostrar_validacion(resultado, "La columna 'MODALIDAD' no tiene valores vacíos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)
        # Validar que contenga valores permitidos
        modalidades_permitidas = ["PRESENCIAL", "VIRTUAL", "SEMIPRESENCIAL"]
        total_validaciones += 1
        resultado, mensaje, detalles = validar_valores(oferta_df, columna_modalidad, modalidades_permitidas)
        observacion = mostrar_validacion(resultado, "La columna 'MODALIDAD' tiene valores válidos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

    # Validación de fechas
    for fecha_col_base in ['FECHA INICIO CURSO', 'FECHA FIN CURSO', 'FECHA ENTREGA DE NOTA']:
        col_fecha = obtener_columna(oferta_df, fecha_col_base)
        if col_fecha:
            total_validaciones += 1
            resultado, mensaje, detalles = validar_fecha(oferta_df, col_fecha)
            observacion = mostrar_validacion(resultado, f"La columna '{col_fecha}' tiene fechas válidas.", mensaje, detalles)
            if resultado:
                validaciones_exitosas += 1
            elif observacion:
                observaciones.append(observacion)

    # Validación de horarios de inicio y fin
    col_inicio = obtener_columna(oferta_df, 'HORA INICIO')
    col_fin = obtener_columna(oferta_df, 'HORA FIN')
    if col_inicio and col_fin:
        total_validaciones += 1
        resultado, mensaje, detalles = validar_horarios(oferta_df, col_inicio, col_fin)
        observacion = mostrar_validacion(resultado, "Los horarios son válidos.", mensaje, detalles)
        if resultado:
            validaciones_exitosas += 1
        elif observacion:
            observaciones.append(observacion)

    # Resumen de validaciones exitosas
    porcentaje_exitosas = (validaciones_exitosas / total_validaciones) * 100 if total_validaciones > 0 else 0
    st.write("### Resumen de Validaciones")
    st.progress(porcentaje_exitosas / 100)
    st.write(f"Validaciones exitosas: {validaciones_exitosas}/{total_validaciones}")
    st.write(f"Porcentaje de validaciones exitosas: {porcentaje_exitosas:.2f}%")

    # Mostrar observaciones detalladas
    if observaciones:
        st.write("### Observaciones de Errores")
        for obs in observaciones:
            if obs:
                st.write(f"- {obs}")

else:
    st.write("Por favor, sube ambos archivos para continuar.")
