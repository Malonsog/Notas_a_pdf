import os
import glob
import markdown
import pdfkit
import re
import yaml

def cargar_metadatos(ruta_metadatos):
    """Carga los metadatos del documento desde un archivo YAML."""
    with open(ruta_metadatos, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def obtener_archivos_markdown(directorio, extension="*.md"):
    """Obtiene una lista de archivos Markdown en el directorio especificado."""
    ruta_busqueda = os.path.join(directorio, extension)
    archivos = glob.glob(ruta_busqueda)
    archivos.sort()  # Ordenar los archivos alfabéticamente
    return archivos

def ajustar_rutas_imagenes(contenido_md, ruta_actual):
    """Ajusta las rutas de las imágenes en el contenido Markdown."""
    patron_imagen = r'!\[.*?\]\((.*?)\)'
    def reemplazar(match):
        ruta_imagen = match.group(1)
        if not ruta_imagen.startswith('http') and not os.path.isabs(ruta_imagen):
            ruta_nueva = os.path.abspath(os.path.join(ruta_actual, ruta_imagen))
            ruta_nueva = ruta_nueva.replace('\\', '/')  # Para compatibilidad con wkhtmltopdf en Windows
            return f'![]({ruta_nueva})'
        else:
            return match.group(0)
    contenido_ajustado = re.sub(patron_imagen, reemplazar, contenido_md)
    return contenido_ajustado

def combinar_markdown_a_html(archivos, ruta_css=None, ruta_logo=None, metadatos=None):
    """Combina varios archivos Markdown en un solo HTML."""
    # Construir el encabezado HTML
    html_head = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n"
    if ruta_css and os.path.exists(ruta_css):
        with open(ruta_css, 'r', encoding='utf-8') as f:
            css = f.read()
            html_head += f"<style>\n{css}\n</style>\n"
    html_head += "</head>\n<body>\n"

    # Final del archivo HTML
    html_tail = "\n</body>\n</html>"

    # Generar la portada
    portada = html_head
    if metadatos:
        portada += "<div class='portada'>\n"
        if 'logo' in metadatos:
            # Construir la ruta completa al archivo del logo
            ruta_logotipo = os.path.join(ruta_logo, metadatos['logo'])
            if os.path.exists(ruta_logotipo):
                ruta_logotipo = os.path.abspath(ruta_logotipo).replace('\\', '/')
                portada += f"<img src='file:///{ruta_logotipo}' alt='Logotipo' class='logo'>\n"
        if 'codigo' in metadatos:
            portada += "\n \n"
            portada += f"<h3>{metadatos['codigo']}:</h3>\n"
        if 'curso' in metadatos:
            portada += f"<h1>{metadatos['curso']}</h1>\n"
        if 'institucion' in metadatos:
            portada += f"<h3>{metadatos['institucion']}</h3>\n"
        if 'fecha' in metadatos:
            portada += f"<p>{metadatos['fecha']}</p>\n"
        portada += "</div>\n"
    portada += html_tail
    
    # Generar el contenido principal
    cuerpo = html_head
    # Placeholder para la TOC
    cuerpo += "<h1>Tabla de Contenidos</h1>\n<div class='toc'>{{TOC}}</div>\n"
    # Agregar un salto de página después de la TOC
    cuerpo += '<div class="salto-pagina"></div>\n'

    # Combinar el contenido de los archivos
    md = markdown.Markdown(
        extensions=["extra", "toc", "tables"],
        extension_configs={
            "toc": {
                "toc_depth": "1-2",  # Incluye encabezados de nivel 1 y 2 en TOC
            }
        },
    )

    for index, archivo in enumerate(archivos):
        ruta_actual = os.path.dirname(archivo)
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido_md = f.read()
            contenido_md = ajustar_rutas_imagenes(contenido_md, ruta_actual)
            html_contenido = md.convert(contenido_md)
            cuerpo += html_contenido + "\n"
            # Insertar salto de página después de cada archivo excepto el último
            if index < len(archivos) - 1:
                cuerpo += '<div style="page-break-after: always;"></div>\n'
    
    # Reemplazar el placeholder con la TOC generada
    toc_html = md.toc
    cuerpo = cuerpo.replace('{{TOC}}', toc_html)

    cuerpo += html_tail

    return portada, cuerpo

def convertir_html_a_pdf(portada, cuerpo, salida_pdf, ruta_html):
    """Convierte contenido HTML a PDF usando pdfkit, incluyendo números de página (excepto en la portada)."""
    opciones_pdf = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '1in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
        # Opciones para el pie de página en el contenido principal
        'footer-right': 'Página [page] de [toPage]',
        'footer-font-size': '9',
        'footer-spacing': '5',
        'footer-line': '',
        # ... otras opciones ...
        'page-offset': '-1'  # Resta 1 al número de página
    }

    # Rutas para guardar los archivos HTML
    ruta_portada = os.path.join(ruta_html, 'portada.html')
    ruta_cuerpo = os.path.join(ruta_html, 'cuerpo.html')

    # Asegurarse de que la carpeta existe
    if not os.path.exists(ruta_html):
        os.makedirs(ruta_html)

    # Guardar el archivo HTML de la portada
    with open(ruta_portada, 'w', encoding='utf-8') as f:
        f.write(portada)

    # Guardar el archivo HTML del cuerpo
    with open(ruta_cuerpo, 'w', encoding='utf-8') as f:
        f.write(cuerpo)

    # Configurar la ruta a wkhtmltopdf si no está en el PATH
    # ruta_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Cambia esta ruta si es necesario
    config = config = pdfkit.configuration()

    # Generar el PDF con la portada y el contenido principal
    pdfkit.from_file(
        ruta_cuerpo,
        salida_pdf,
        options=opciones_pdf,
        configuration=config,
        cover=ruta_portada
    )

def main():
    directorio_markdown = "./contenido"           # Directorio con los archivos Markdown
    ruta_css = "./estilos/estilo.css"             # Ruta al archivo CSS
    ruta_metadatos = "./metadatos/metadatos.yaml" # Ruta al archivo de datos
    ruta_logo = "./logo"                          # Ruta al logotipo para la portada
    ruta_html = "./html"                          # Ruta para el archivo HTML generado
    salida_pdf = "documento_combinado.pdf"        # Nombre del archivo PDF final

    # Cargar los metadatos del documento
    metadatos = cargar_metadatos(ruta_metadatos)

    archivos = obtener_archivos_markdown(directorio_markdown)
    if not archivos:
        print(f"No se encontraron archivos Markdown en el directorio {directorio_markdown}.")
        return

    print(f"{len(archivos)} archivos Markdown encontrados en el directorio {directorio_markdown}")

    # Obtener el HTML de la portada y del contenido principal
    portada, cuerpo = combinar_markdown_a_html(archivos, ruta_css, ruta_logo, metadatos)

    # Convertir HTML a PDF
    convertir_html_a_pdf(portada, cuerpo, salida_pdf, ruta_html)

    print(f"PDF generado exitosamente: {salida_pdf}")

if __name__ == "__main__":
    main()
