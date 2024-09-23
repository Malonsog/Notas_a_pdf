# Pasar Notas a PDF

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)

Siempre he tenido la costumbre de tomar notas en archivos de texto simples cuando estudio, ya que un bloc de notas es la herramienta más sencilla y siempre está disponible. Con el tiempo, estas notas se han vuelto más complejas, y comencé a utilizar Markdown para resaltar títulos y subtítulos, y ocasionalmente agregar imágenes.

Este proyecto es un script en Python que combina múltiples archivos Markdown en un único documento PDF con una portada personalizada, tabla de contenidos automática y números de página. Es útil para crear documentos extensos, como apuntes de cursos, manuales o libros, a partir de archivos Markdown individuales.

## Características

- **Combina archivos Markdown** desde un directorio especificado en un solo documento PDF.
- **Genera una portada personalizada** utilizando metadatos como el nombre del curso, fecha, institución, etc.
- **Crea una tabla de contenidos (TOC) automática** basada en los encabezados de los archivos Markdown.
- **Inserta números de página** en el PDF final.
- **Ajusta rutas de imágenes** para asegurar que se muestren correctamente en el PDF.
- **Utiliza un archivo de configuración YAML** para especificar metadatos.
- **Aplica estilos personalizados** mediante un archivo CSS.

## Requisitos

- **Python 3.x**
- `wkhtmltopdf` instalado y accesible en el PATH del sistema.
- **Paquetes de Python**:

  - `markdown`
  - `pdfkit`
  - `PyYAML`

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Malonsog/Notas_a_pdf.git

cd Notas_a_pdf
```

### 2. Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv .venv

# En Windows
.venv\Scripts\activate

# En Unix o MacOS
source .venv/bin/activate
```

### 3. Instalar las dependencias de Python

Usando requirements.txt

```bash
pip install -r requirements.txt
```

O instalando los paquetes manualmente

```bash
pip install markdown pdfkit PyYAML
```

### 4. Instalar wkhtmltopdf

Descarga `wkhtmltopdf` desde [wkhtmltopdf.org](https://wkhtmltopdf.org/) y sigue las instrucciones de instalación para tu sistema operativo.

**En Windows:** Asegúrate de agregar el directorio de `wkhtmltopdf` al **PATH** del sistema durante la instalación o especifica la ruta en el script si es necesario.

## Uso

1. Coloca tus archivos Markdown en el directorio **/contenido**. Asegúrate de que los archivos:
    - Tengan la extensión **.md**.
    - Utilicen correctamente los encabezados **(#, ##, etc.)** para que se incluyan en la tabla de contenidos.
    - Las imágenes y recursos referenciados tengan rutas relativas correctas.

2. Ejecuta el script **pasar_notas_a_pdf.py**:

```bash
python pasar_notas_a_pdf.py
```

Esto generará un archivo PDF llamado **documento_combinado.pdf** en el directorio actual, con el contenido de los archivos combinados y una tabla de contenidos en base a los títulos.

### Argumentos Disponibles

- `--sin-portada`: No incluir la portada en el PDF.
- `--sin-toc`: No incluir la tabla de contenidos.
- `--sin-numeracion`: No incluir números de página en el PDF.
- `--guardar-html`: Guardar los archivos HTML generados.
- `--directorio [ruta]`: Especifica el directorio con los archivos Markdown (por defecto `./contenido`).
- `--css [ruta]`: Ruta al archivo CSS para estilizar el documento (por defecto `./estilos/estilo.css`).
- `--metadatos [ruta]`: Ruta al archivo de metadatos YAML para la portada (por defecto `./metadatos/metadatos.yaml`).
- `--logo [ruta]`: Ruta al directorio del logotipo para la portada (por defecto `./logo`).
- `--salida [nombre]`: Nombre del archivo PDF de salida (por defecto `documento_combinado.pdf`).

### Ejemplos de uso

- **Generar PDF con configuración por defecto:**

```bash
python pasar_notas_a_pdf.py
```

- **Generar PDF sin portada y sin tabla de contenidos::**

```bash
python pasar_notas_a_pdf.py --sin-portada --sin-toc
```

- **Generar PDF sin numeración de páginas:**

```bash
python pasar_notas_a_pdf.py --sin-numeracion
```

- **Especificar directorio de archivos y nombre de salida:**

```bash
python pasar_notas_a_pdf.py --directorio ./mis_notas --salida mis_apuntes.pdf
```

- **Guardar los archivos HTML generados:**

```bash
python pasar_notas_a_pdf.py --guardar-html
```

### Ayuda adicional

Para ver una descripción completa de los argumentos disponibles y obtener ayuda sobre cómo utilizar el script, ejecuta:

```bash
python pasar_notas_a_pdf.py --help
```

## Estructura por defecto

```graphql
├── contenido                 # Directorio con los archivos Markdown
│   ├── capitulo1.md
│   ├── capitulo2.md
│   └── ...
├── estilos
│   └── estilo.css            # Archivo CSS con los estilos personalizados
├── html                      # Directorio para los archivos HTML generados
│   └── cuerpo.html           # Archivo HTML con el contenido (generado)
│   └── portada.html          # Archivo HTML con la portada (generado)
├── img                       # Directorio con las imagenes del contenido
│   ├── imagen1.png
│   ├── imagen2.png
│   └── ...
├── logo
│   └── logo.png              # Logotipo para la portada (opcional)
├── metadatos
│   └── metadatos.yaml        # Archivo YAML con los metadatos del documento (opcional)
├── pasar_notas_a_pdf.py      # Script principal
├── README.md                 # Este archivo
└── requirements.txt          # Archivo con las dependencias de Python requeridas
```

## Configuración y personalización

### Metadatos

Edita el archivo **metadatos/metadatos.yaml** para especificar los metadatos del documento:

```yaml
curso: "Nombre del Curso"
institucion: "Nombre de la Institución"
fecha: "Fecha del Documento"
logo: "logo.png"
# etc.
```

### Estilos

Puedes personalizar los estilos del documento modificando el archivo **estilos/estilo.css**.

### Modificar Rutas y Nombres de Archivos

Puedes cambiar las rutas de los directorios y los nombres de los archivos utilizando los argumentos de línea de comandos al ejecutar el script, sin necesidad de editar el código fuente. Los argumentos disponibles son:

- `--directorio [ruta]`: Especifica el directorio con los archivos Markdown (por defecto `./contenido`).
- `--css [ruta]`: Ruta al archivo CSS para estilizar el documento (por defecto `./estilos/estilo.css`).
- `--metadatos [ruta]`: Ruta al archivo de metadatos YAML para la portada (por defecto `./metadatos/metadatos.yaml`).
- `--logo [ruta]`: Ruta al directorio del logotipo para la portada (por defecto `./logo`).
- `--salida [nombre]`: Nombre del archivo PDF de salida (por defecto `documento_combinado.pdf`).

**Ejemplo:**

```bash
python pasar_notas_a_pdf.py --directorio ./mis_notas --css ./estilos/mi_estilo.css --metadatos ./mis_metadatos.yaml --logo ./imagenes/logo --salida mi_documento.pdf
```

Esto permite una mayor flexibilidad y evita la necesidad de modificar el código del script cada vez que desees cambiar estas configuraciones.

### Ajustar la Profundidad de la Tabla de Contenidos

Puedes ajustar la profundidad de los encabezados incluidos en la tabla de contenidos modificando el parámetro **toc_depth** en la función **combinar_markdown_a_html**:

```python
md = markdown.Markdown(
    extensions=["extra", "toc", "tables"],
    extension_configs={
        "toc": {
            "toc_depth": "1-3",  # Incluye encabezados de nivel 1 a 3
        }
    },
)
```

## Notas

### Especificar la Ruta de wkhtmltopdf

Si `wkhtmltopdf` no está en el **PATH** del sistema, puedes especificar la ruta en el script:

```python
config = pdfkit.configuration(wkhtmltopdf=r"C:\ruta\a\wkhtmltopdf.exe")
```

### Imágenes en los Archivos Markdown

El script ajusta las rutas de las imágenes para que se muestren correctamente en el **PDF**. Asegúrate de que las imágenes están referenciadas con rutas relativas y que los archivos existen.

### Portada del Documento

Si en los metadatos especificas el nombre de la imagen para el logotipo, éste se incluirá en la portada del documento. Asegúrate de que la ruta es correcta y el archivo exista.

### Salto de Página entre Secciones

El script inserta saltos de página entre cada archivo Markdown y después de la portada y la tabla de contenidos, asegurando que cada sección comience en una nueva página.

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes sugerencias, encuentras errores o quieres agregar nuevas funcionalidades, por favor abre un issue o un pull request.
