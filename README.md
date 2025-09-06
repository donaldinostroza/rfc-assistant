# Extractor de Licitaciones y Órdenes de Compra de Mercado Público Chile

## 1. Resumen del Proyecto

Este proyecto es un sistema automatizado para extraer, almacenar y visualizar datos de licitaciones públicas (RFCs) y órdenes de compra del portal de Mercado Público de Chile. Utiliza un conjunto de scripts de Python y se ejecuta diariamente a través de GitHub Actions para mantener los datos actualizados. El resultado final es una página web estática, alojada en GitHub Pages, que muestra las últimas licitaciones y órdenes de compra en una tabla clara y legible.

El sistema está diseñado para ser de bajo costo (presupuesto cero), utilizando únicamente servicios gratuitos de GitHub.

## 2. Cómo Funciona

El núcleo del proyecto es un flujo de trabajo (workflow) de GitHub Actions que se ejecuta automáticamente una vez al día. Este flujo realiza los siguientes pasos:

1. **Extracción de Datos:** Un script de Python (`extractor.py`) se conecta a la API de Mercado Público y descarga las licitaciones (RFCs) y órdenes de compra publicadas el día anterior.
2. **Almacenamiento Persistente:** Los datos extraídos se guardan en una base de datos de archivo, SQLite (`licitaciones.db`). Esta base de datos se almacena directamente en el repositorio de Git.
3. **Generación de la Página Web:** Otro script de Python (`generate_html.py`) lee los datos de la base de datos SQLite y genera una página web estática (`index.html`) que contiene una tabla con las últimas 100 licitaciones y órdenes de compra.
4. **Actualización del Repositorio:** El flujo de trabajo finaliza haciendo `commit` y `push` de los archivos actualizados (`licitaciones.db` e `index.html`) de vuelta al repositorio.
5. **Publicación:** GitHub Pages sirve automáticamente el archivo `index.html` actualizado, haciendo que los datos más recientes sean visibles en la web.

> Este ciclo asegura que tanto los datos crudos como la visualización se actualicen diariamente sin intervención manual.

## 3. Componentes del Proyecto

- `extractor.py`: Script principal de extracción. Se conecta a la API, maneja la paginación (si fuera necesario) y guarda los datos en la base de datos SQLite. Lee la credencial de la API desde un Secret de GitHub para mayor seguridad. Extrae tanto licitaciones (RFCs) como órdenes de compra.
- `generate_html.py`: Script de visualización. Lee los datos desde `licitaciones.db` usando la librería pandas y genera un archivo `index.html` con una tabla estilizada.
- `licitaciones.db`: El archivo de la base de datos SQLite. Actúa como el almacenamiento persistente del proyecto. Contiene dos tablas: `rfcs` para licitaciones y `purchase_orders` para órdenes de compra.
- `index.html`: La página web estática generada que se muestra a los usuarios finales a través de GitHub Pages.
- `.github/workflows/run-extractor.yml`: Archivo de configuración que define el flujo de trabajo de GitHub Actions, incluyendo el horario de ejecución (cron), los pasos a seguir y los permisos necesarios para escribir en el repositorio.
- `requirements.txt`: Archivo que lista las dependencias de Python necesarias para el proyecto (`requests`, `pandas`).

## 4. Configuración para Replicar el Proyecto

Para que otro usuario o LLM pueda configurar una copia de este proyecto, se deben seguir estos pasos:

1. **Fork del Repositorio:** Clonar o hacer un "fork" de este repositorio.
2. **Obtener un Ticket de API:** Solicitar un `API_TICKET` en el portal de [api.mercadopublico.cl](https://api.mercadopublico.cl).
3. **Configurar el Secret:** En la configuración del repositorio de GitHub, ir a `Settings > Secrets and variables > Actions` y crear un nuevo "repository secret" con el nombre `API_TICKET` y el valor de la credencial obtenida.
4. **Activar GitHub Pages:** En la configuración del repositorio, ir a `Settings > Pages` y activar el despliegue desde la rama principal (`main` o `master`).

## 5. Pila Tecnológica (Tech Stack)

- **Lenguaje:** Python 3.10
- **Librerías Principales:** `requests`, `pandas`
- **Base de Datos:** SQLite
- **Automatización:** GitHub Actions
- **Alojamiento Web:** GitHub Pages