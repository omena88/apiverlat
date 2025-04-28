# FastAPI Template

Este es un proyecto de plantilla para FastAPI que incluye:

*   **FastAPI**: Framework web moderno y rápido para construir APIs con Python 3.7+.
*   **Uvicorn**: Servidor ASGI ultrarrápido.
*   **Dockerfile**: Para construir una imagen Docker de la aplicación.
*   **requirements.txt**: Lista de dependencias de Python.

## Estructura del Proyecto

```
/
|-- apiVerlat/
|   |-- main.py             # Punto de entrada principal de la aplicación FastAPI
|   |-- requirements.txt    # Dependencias de Python
|   |-- Dockerfile          # Configuración para construir la imagen Docker
|   |-- README.md           # Este archivo
|   |-- programacion_39.xlsx # Archivo de entrada de datos (debes añadirlo)
|-- .env                  # (Opcional) Variables de entorno
|-- .gitignore            # (Opcional) Archivos a ignorar por Git
```

## Requisitos Previos

*   Python 3.7+
*   pip (Administrador de paquetes de Python)
*   Docker (Opcional, para ejecución en contenedores)

## Instalación y Ejecución Local

1.  **Clonar el repositorio (si aplica):**
    ```bash
    git clone <tu-repositorio>
    cd apiVerlat
    ```

2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Añadir el archivo de entrada:**
    *   Coloca tu archivo `programacion_39.xlsx` dentro de la carpeta `apiVerlat`.

5.  **Ejecutar la aplicación con Uvicorn:**
    ```bash
    uvicorn main:app --reload
    ```
    *   `main`: se refiere al archivo `main.py`.
    *   `app`: es el objeto `FastAPI` creado dentro de `main.py` (`app = FastAPI()`)
    *   `--reload`: hace que el servidor se reinicie automáticamente después de cambios en el código (ideal para desarrollo).

    La API estará disponible en `http://127.0.0.1:8000`.

## Endpoints de la API

*   **`GET /programacion`**: Devuelve los datos procesados de las hojas "Programación" y "Calendario" del archivo Excel en formato JSON.
*   **`GET /docs`**: Interfaz interactiva de documentación de la API (Swagger UI).
*   **`GET /redoc`**: Documentación alternativa de la API (ReDoc).

## Ejecución con Docker (Opcional)

1.  **Construir la imagen Docker:**
    Asegúrate de que el archivo `programacion_39.xlsx` esté en la carpeta `apiVerlat` antes de construir.
    ```bash
    docker build -t mi-api-verlat .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -d -p 8000:8000 --name contenedor-api-verlat mi-api-verlat
    ```
    *   `-d`: Ejecuta el contenedor en segundo plano.
    *   `-p 8000:8000`: Mapea el puerto 8000 del host al puerto 8000 del contenedor.
    *   `--name`: Asigna un nombre al contenedor para facilitar su gestión.

    La API estará disponible en `http://localhost:8000` (o la IP de tu Docker host).

3.  **Ver logs (si es necesario):**
    ```bash
    docker logs contenedor-api-verlat
    ```

4.  **Detener el contenedor:**
    ```bash
    docker stop contenedor-api-verlat
    ```

5.  **Eliminar el contenedor:**
    ```bash
    docker rm contenedor-api-verlat
    ```

## Personalización

*   Modifica `main.py` para añadir más endpoints o cambiar la lógica existente.
*   Actualiza `requirements.txt` si añades nuevas dependencias (`pip freeze > requirements.txt`).
*   Ajusta el `Dockerfile` si necesitas configuraciones específicas del contenedor. 