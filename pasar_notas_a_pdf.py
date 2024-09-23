import os
import glob
import markdown
import pdfkit
import re
import yaml
import argparse


def cargar_metadatos(ruta_metadatos):
    """Carga los metadatos del documento desde un archivo YAML si existe."""
    if os.path.exists(ruta_metadatos):
        with open(ruta_metadatos, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    else:
        print(f"No se encontraron metadatos en {ruta_metadatos}.")
        return None


def obtener_archivos_markdown(directorio, extension="*.md"):
    """Obtiene una lista de archivos Markdown en el directorio especificado."""
    ruta_busqueda = os.path.join(directorio, extension)
    archivos = glob.glob(ruta_busqueda)
    archivos.sort()  # Ordenar los archivos alfabéticamente
    return archivos


def ajustar_rutas_imagenes(contenido_md, ruta_actual):
    """Ajusta las rutas de las imágenes en el contenido Markdown."""
    patron_imagen = r"!\[.*?\]\((.*?)\)"

    def reemplazar(match):
        ruta_imagen = match.group(1)
        if not ruta_imagen.startswith("http") and not os.path.isabs(ruta_imagen):
            ruta_nueva = os.path.abspath(os.path.join(ruta_actual, ruta_imagen))
            ruta_nueva = ruta_nueva.replace(
                "\\", "/"
            )  # Para compatibilidad con wkhtmltopdf en Windows
            return f"![]({ruta_nueva})"
        else:
            return match.group(0)

    contenido_ajustado = re.sub(patron_imagen, reemplazar, contenido_md)
    return contenido_ajustado


def combinar_markdown_a_html(archivos, ruta_css=None, ruta_logo=None, metadatos=None, incluir_toc=True):
    """Combina varios archivos Markdown en HTML para la portada y el contenido principal."""
    # Construir el encabezado HTML
    html_head = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n"
    if ruta_css and os.path.exists(ruta_css):
        with open(ruta_css, 'r', encoding='utf-8') as f:
            css = f.read()
            html_head += f"<style>\n{css}\n</style>\n"
    html_head += "</head>\n<body>\n"

    # Final del archivo HTML
    html_tail = "\n</body>\n</html>"

    # Generar la portada solo si hay metadatos
    portada = None
    if metadatos:
        portada = html_head
        portada += "<div class='portada'>\n"
        if "logo" in metadatos:
            # Construir la ruta completa al archivo del logo
            ruta_logotipo = os.path.join(ruta_logo, metadatos["logo"])
            if os.path.exists(ruta_logotipo):
                ruta_logotipo = os.path.abspath(ruta_logotipo).replace("\\", "/")
                portada += (
                    f"<img src='file:///{ruta_logotipo}' alt='Logotipo' class='logo'>\n"
                )
        if "codigo" in metadatos:
            portada += "\n \n"
            portada += f"<h3>{metadatos['codigo']}:</h3>\n"
        if "curso" in metadatos:
            portada += f"<h1>{metadatos['curso']}</h1>\n"
        if "institucion" in metadatos:
            portada += f"<h3>{metadatos['institucion']}</h3>\n"
        if "fecha" in metadatos:
            portada += f"<p>{metadatos['fecha']}</p>\n"
        portada += "</div>\n"
        portada += html_tail

    # Generar el contenido principal
    cuerpo = html_head

    # Incluir TOC si se especifica
    if incluir_toc:
        # Placeholder para la TOC
        cuerpo += "<h1>Tabla de Contenidos</h1>\n<div class='toc'>{{TOC}}</div>\n"
        # Agregar un salto de página después de la TOC
        cuerpo += '<div class="salto-pagina"></div>\n'

    # Combinar el contenido de los archivos
    md_extensions = ["extra", "tables"]
    if incluir_toc:
        md_extensions.append("toc")

    md = markdown.Markdown(
        extensions=md_extensions,
        extension_configs={
            "toc": {
                "toc_depth": "1-2",  # Incluye encabezados de nivel 1 y 2 en TOC
            }
        } if incluir_toc else {},
    )

    for index, archivo in enumerate(archivos):
        ruta_actual = os.path.dirname(archivo)
        with open(archivo, "r", encoding="utf-8") as f:
            contenido_md = f.read()
            contenido_md = ajustar_rutas_imagenes(contenido_md, ruta_actual)
            html_contenido = md.convert(contenido_md)
            cuerpo += html_contenido + "\n"
            # Insertar salto de página después de cada archivo excepto el último
            if index < len(archivos) - 1:
                cuerpo += '<div style="page-break-after: always;"></div>\n'

    # Reemplazar el placeholder con la TOC generada si se incluyó
    if incluir_toc:
        toc_html = md.toc
        cuerpo = cuerpo.replace('{{TOC}}', toc_html)

    cuerpo += html_tail

    return portada, cuerpo


def convertir_html_a_pdf(portada, cuerpo, salida_pdf, ruta_html, metadatos, incluir_portada=True, numerar_paginas=True, guardar_html=False):
    """Convierte contenido HTML a PDF usando pdfkit, con opciones para portada y numeración de páginas."""
    opciones_pdf = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '1in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'enable-local-file-access': '',
    }

    # Opciones para el pie de página si se numeran las páginas
    if numerar_paginas:
        opciones_pdf.update({
            'footer-right': 'Página [page] de [toPage]',
            'footer-font-size': '9',
            'footer-spacing': '5',
            'footer-line': '',
        })

    # Rutas para guardar los archivos HTML
    ruta_cuerpo = os.path.join(ruta_html, 'cuerpo.html')

    # Asegurarse de que la carpeta existe
    if not os.path.exists(ruta_html):
        os.makedirs(ruta_html)

    # Guardar el archivo HTML del cuerpo
    with open(ruta_cuerpo, 'w', encoding='utf-8') as f:
        f.write(cuerpo)

    # Configurar la ruta a wkhtmltopdf si no está en el PATH
    config = pdfkit.configuration()

    # Si hay portada y se incluye, ajustamos opciones
    if portada and incluir_portada:
        ruta_portada = os.path.join(ruta_html, 'portada.html')
        with open(ruta_portada, 'w', encoding='utf-8') as f:
            f.write(portada)
        # Ajustar la numeración si se numeran las páginas
        if numerar_paginas:
            opciones_pdf['page-offset'] = '-1'  # Resta 1 al número de página

        # Generar el PDF con la portada
        pdfkit.from_file(
            ruta_cuerpo,
            salida_pdf,
            options=opciones_pdf,
            configuration=config,
            cover=ruta_portada
        )
    else:
        # Sin portada
        if numerar_paginas:
            opciones_pdf['page-offset'] = '0'
        # Generar el PDF sin portada
        pdfkit.from_file(
            ruta_cuerpo,
            salida_pdf,
            options=opciones_pdf,
            configuration=config
        )

    # Eliminar los archivos HTML si no se deben guardar
    if not guardar_html:
        os.remove(ruta_cuerpo)
        if portada and incluir_portada:
            os.remove(ruta_portada)


def main():
    # Configurar el analizador de argumentos
    parser = argparse.ArgumentParser(description='Genera un PDF a partir de archivos Markdown.')

    # Definir los argumentos existentes y agregar el nuevo
    parser.add_argument('--sin-portada', action='store_true', help='No incluir la portada en el PDF.')
    parser.add_argument('--sin-toc', action='store_true', help='No incluir la tabla de contenidos.')
    parser.add_argument('--sin-numeracion', action='store_true', help='No incluir números de página en el PDF.')
    parser.add_argument('--guardar-html', action='store_true', help='Guardar los archivos HTML generados.')
    parser.add_argument('--directorio', default='./contenido', help='Directorio que contiene los archivos Markdown.')
    parser.add_argument('--css', default='./estilos/estilo.css', help='Ruta al archivo CSS.')
    parser.add_argument('--metadatos', default='./metadatos/metadatos.yaml', help='Ruta al archivo de metadatos.')
    parser.add_argument('--logo', default='./logo', help='Ruta al directorio del logotipo.')
    parser.add_argument('--salida', default='documento_combinado.pdf', help='Nombre del archivo PDF de salida.')

    # Analizar los argumentos
    args = parser.parse_args()

    # Variables basadas en los argumentos
    directorio_markdown = args.directorio
    ruta_css = args.css
    ruta_metadatos = args.metadatos
    ruta_logo = args.logo
    ruta_html = "./html"  # Puedes hacerlo opcional si lo deseas
    salida_pdf = args.salida

    # Cargar los metadatos del documento solo si se incluye la portada
    if not args.sin_portada:
        metadatos = cargar_metadatos(ruta_metadatos)
    else:
        metadatos = None

    archivos = obtener_archivos_markdown(directorio_markdown)
    if not archivos:
        print(f"No se encontraron archivos Markdown en el directorio {directorio_markdown}.")
        return

    print(f"{len(archivos)} archivos Markdown encontrados en el directorio {directorio_markdown}")

    # Obtener el HTML de la portada y del contenido principal
    portada, cuerpo = combinar_markdown_a_html(
        archivos,
        ruta_css,
        ruta_logo,
        metadatos,
        incluir_toc=not args.sin_toc
    )

    # Convertir HTML a PDF
    convertir_html_a_pdf(
        portada,
        cuerpo,
        salida_pdf,
        ruta_html,
        metadatos,
        incluir_portada=not args.sin_portada,
        numerar_paginas=not args.sin_numeracion,
        guardar_html=args.guardar_html
    )


    print(f"PDF generado exitosamente: {salida_pdf}")


if __name__ == "__main__":
    main()
