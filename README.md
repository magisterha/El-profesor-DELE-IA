# 🎓 DELE Tutor AI

**Un sistema inteligente de entrenamiento para el examen DELE de español (Niveles A1-C2).**

Esta aplicación utiliza **Gemini 2.5 Flash Lite** para simular un tutor nativo que adapta su pedagogía según el nivel del estudiante, desde explicaciones bilingües para principiantes hasta debates socráticos para niveles avanzados.

## 🚀 Características

* **Arquitectura Multinivel:** 6 niveles de competencia (A1-C2) con metodología diferenciada.
* **Pantalla Dividida Inteligente:** Chat a la izquierda, Pizarra Gramatical a la derecha (detecta explicaciones automáticamente).
* **Feedback PDF:** Genera un informe de diagnóstico descargable al final de la sesión.
* **Modo Diagnóstico:** Detecta el nivel del usuario si no sabe cuál elegir.
* **Interfaz Multilingüe:** Disponible en Español, Inglés y Chino Tradicional.

## 📂 Estructura del Currículo

El sistema carga dinámicamente 30 escenarios pedagógicos:

| Nivel | Enfoque Pedagógico | Temas Ejemplo |
| :--- | :--- | :--- |
| **A1** | Bucle de Fundación Bilingüe (Instrucciones en Chino) | Presentarse, Cafetería, Familia |
| **A2** | Puente de Transición | Rutina (Reflexivos), Pasado (Indef/Imp) |
| **B1** | Activación Anti-Memorización | Ocio, Trabajo, Compras |
| **B2** | Taller Retórico (Argumentación) | Turismo de Masas, Inteligencia Artificial |
| **C1** | Taller de Persuasión (Matiz y Registro) | Ecología, Estilo Enfático |
| **C2** | Laboratorio de Estilo (Nativo Culto) | Sátira, Diplomacia Extrema, Modismos |

## 🛠️ Instalación Local

1.  Clona el repositorio.
2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configura tu API Key de Google:
    ```bash
    export GOOGLE_API_KEY="tu_api_key_aqui"
    ```
4.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

## ☁️ Despliegue

Este proyecto está diseñado para desplegarse en **Streamlit Cloud**.
