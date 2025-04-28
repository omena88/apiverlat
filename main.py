import pandas as pd
import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
import os
import io # Para manejar el archivo en memoria
import xlsxwriter # Para crear el archivo Excel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# --- Configuración de plantillas Jinja2 ---
templates = Jinja2Templates(directory="templates")

# --- Mapeo de operadores y meses (constantes) ---
operator_list = [
    "CHUCO MAYTA JUAN",
    "DIAZ PALACIOS ANGEL",
    "RODRIGUEZ CHUCO JOSE",
    "MORENO ASTETE ABILIO",
    "YAPIAS INGA JESÚS",
    "HINOSTROZA QUISPE DANILO YORDIN",
    "SUSANIBAR MIRANDA DAVID"
]
operator_numbers = {name: idx+1 for idx, name in enumerate(operator_list)}

meses_esp = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

app = FastAPI()

# --- Endpoint para servir la página HTML de carga ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Sirve la página HTML principal con el formulario de carga."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/programacion")
async def process_and_generate_excel(file: UploadFile = File(...)):
    """
    Endpoint para recibir un archivo Excel de programación, procesarlo y
    devolver un nuevo archivo Excel generado.
    Espera un archivo llamado 'file' en la petición POST multipart/form-data.
    """
    # Verificar si es un archivo Excel
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Se requiere .xlsx o .xls")

    try:
        # Leemos el contenido del archivo cargado en memoria
        content = await file.read()
        # Usamos io.BytesIO para que pandas pueda leer desde el contenido en memoria
        input_file_like = io.BytesIO(content)

        # --- 1. Cargar datos desde el archivo en memoria ---
        df = pd.read_excel(input_file_like, sheet_name='Horarios', parse_dates=['Fecha'])
        # Asegurarnos de cerrar el buffer de entrada después de leerlo
        input_file_like.close()

        # Resto del procesamiento igual que antes...
        df['Operador'] = df['Operador'].str.strip()
        df['Posición'] = df['Posición'].str.strip()
        df['Fecha'] = df['Fecha'].dt.date

    except Exception as e:
        # Mejoramos el manejo de errores específicos de lectura/procesamiento
        error_detail = f"Error procesando el archivo Excel cargado: {str(e)}"
        if isinstance(e, KeyError):
            error_detail = f"Error en el formato del Excel: No se encontró la columna o la hoja 'Horarios'. Detalles: {str(e)}"
        elif isinstance(e, ValueError):
            error_detail = f"Error en los datos del Excel (posiblemente en fechas). Detalles: {str(e)}"
        raise HTTPException(status_code=422, detail=error_detail) # 422 Unprocessable Entity

    # --- Preparación para crear el Excel de salida en memoria ---
    output_buffer = io.BytesIO()
    # Usamos el modo in_memory para xlsxwriter
    workbook = xlsxwriter.Workbook(output_buffer, {'in_memory': True})

    # --- Lógica de creación del Excel (adaptada del script original) ---

    # Formatos
    fmt_center      = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
    fmt_left        = workbook.add_format({'align': 'left',   'valign': 'vcenter'})
    fmt_bold_center = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
    fmt_bold_left   = workbook.add_format({'bold': True, 'align': 'left',   'valign': 'vcenter'})
    width_day       = 4

    # Definición de meses y días (dentro del endpoint ahora)
    days_in_month = {m: (datetime.date(2025, m % 12 + 1, 1) - datetime.timedelta(days=1)).day for m in range(1, 13)}
    months = [(m, f"{m}. {meses_esp[m]}") for m in range(1, 13)]

    # --- 4.1 Pestaña "Programación" ---
    ws1 = workbook.add_worksheet('Programación')
    col = 2
    for month_num, month_name in months:
        dm = days_in_month[month_num]
        ws1.merge_range(0, col, 0, col + dm - 1, month_name, fmt_bold_center)
        for d in range(1, dm + 1):
            ws1.write(1, col + d - 1, d, fmt_bold_center)
            ws1.set_column(col + d - 1, col + d - 1, width_day)
        ws1.set_column(col + dm, col + dm, 1)
        col += dm + 1
    ws1.write(0, 0, '#', fmt_bold_center)
    ws1.write(0, 1, 'Operador', fmt_bold_center)
    ws1.write(1, 0, '#', fmt_bold_center)
    ws1.write(1, 1, 'Operador', fmt_bold_center)
    row = 2
    for op in operator_list:
        ws1.write(row, 0, operator_numbers[op], fmt_center)
        ws1.write(row, 1, op, fmt_left)
        col = 2
        for month_num, _ in months:
            dm = days_in_month[month_num]
            for d in range(1, dm + 1):
                date = datetime.date(2025, month_num, d)
                sub = df[(df['Operador'] == op) & (df['Fecha'] == date)]
                if not sub.empty:
                    ws1.write(row, col, sub['Estado'].iloc[0], fmt_center)
                col += 1
            col += 1
        row += 1
    ws1.set_column(0, 0, 5)
    ws1.set_column(1, 1, 30)

    # --- 4.2 Pestaña "Calendario" ---
    ws2 = workbook.add_worksheet('Calendario')
    start_row = 0
    # Usamos try/except por si la columna 'Posición' no existe en el archivo subido
    try:
        posiciones = df['Posición'].unique()
    except KeyError:
        posiciones = [] # Si no existe, no generamos esta parte
        print("Advertencia: Columna 'Posición' no encontrada en el archivo subido.")

    for position in posiciones:
        ws2.write(start_row, 0, position, fmt_bold_left)
        ws2.write(start_row+1, 0, 'Mes', fmt_bold_center)
        ws2.write(start_row+1, 1, 'Turno', fmt_bold_center)
        for d in range(1, 32):
            ws2.write(start_row+1, d+1, d, fmt_bold_center)
            ws2.set_column(d+1, d+1, width_day)
        r = start_row + 2
        for month_num, month_name in months:
            dm = days_in_month[month_num]
            for shift in ['TD', 'TN']:
                ws2.write(r, 0, month_name, fmt_left)
                ws2.write(r, 1, shift, fmt_center)
                for d in range(1, dm + 1):
                    date = datetime.date(2025, month_num, d)
                    # Añadimos chequeo de KeyError aquí también
                    try:
                        sub = df[(df['Posición'] == position) & (df['Fecha'] == date) & (df['Estado'] == shift)]
                    except KeyError:
                        sub = pd.DataFrame() # Dataframe vacío si falta alguna columna

                    if not sub.empty:
                        # Añadimos chequeo por si 'Operador' no existe
                        if 'Operador' in sub.columns:
                            num = operator_numbers.get(sub['Operador'].iloc[0])
                            if num is not None:
                                ws2.write(r, d+1, num, fmt_center)
                        else:
                            print(f"Advertencia: Columna 'Operador' no encontrada para fecha {date}, posición {position}, turno {shift}.")
                r += 1
        start_row = r + 1
    ws2.set_column(0, 0, 12)
    ws2.set_column(1, 1, 6)

    # --- Finalizar y preparar para enviar ---
    workbook.close()
    output_buffer.seek(0) # Rebobinar el buffer al principio

    # Usamos el nombre original + sufijo, o un nombre genérico
    base_name = os.path.splitext(file.filename)[0]
    output_filename = f"{base_name}_procesado.xlsx"

    return StreamingResponse(
        output_buffer,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="{output_filename}"'} # Indica al navegador que descargue el archivo
    )

# Para ejecutar localmente con uvicorn: uvicorn apiVerlat.main:app --reload
if __name__ == "__main__":
    import uvicorn
    # Podemos volver al puerto 8000 por defecto si ya no hay conflicto
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Añadir reload=True aquí para consistencia local 