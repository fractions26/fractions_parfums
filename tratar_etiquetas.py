import fitz
from PIL import Image
import io
import os

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

PASTA = r"C:\Users\wwwdl\OneDrive\Documentos\ETIQUETAS"
DESTINO = os.path.join(PASTA, "AJUSTADAS")

os.makedirs(DESTINO, exist_ok=True)

# 100x150 mm
LARGURA = 283.46
ALTURA = 425.20

MARGEM = 2
ESPACO = 3

# resolução para detectar margens
DPI = 500

# aumenta o tamanho sem distorcer
FATOR_ESCALA = 1.40

# ==========================================================

def detectar_area_util(pagina):
    zoom = DPI / 72
    pix = pagina.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        alpha=False
    )

    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    largura, altura = img.size
    pixels = img.load()

    esquerda = largura
    direita = 0
    topo = altura
    baixo = 0

    LIMITE = 245

    for y in range(altura):
        for x in range(largura):
            if pixels[x, y] < LIMITE:
                esquerda = min(esquerda, x)
                direita = max(direita, x)
                topo = min(topo, y)
                baixo = max(baixo, y)

    if direita <= esquerda or baixo <= topo:
        return pagina.rect

    fator = 72 / DPI
    margem = 2

    return fitz.Rect(
        max(0, esquerda * fator - margem),
        max(0, topo * fator - margem),
        min(pagina.rect.width, direita * fator + margem),
        min(pagina.rect.height, baixo * fator + margem)
    )

# ==========================================================

def ampliar(rect, fator):
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2
    w = rect.width * fator
    h = rect.height * fator

    return fitz.Rect(
        cx - w / 2,
        cy - h / 2,
        cx + w / 2,
        cy + h / 2
    )

# ==========================================================

for arquivo in os.listdir(PASTA):
    if not arquivo.lower().endswith(".pdf"):
        continue

    origem = os.path.join(PASTA, arquivo)
    print(f"Processando {arquivo}")

    pdf = fitz.open(origem)
    novo = fitz.open()

    if len(pdf) < 2:
        print("Arquivo ignorado.")
        pdf.close()
        continue

    pagina_etiqueta = pdf[0]
    pagina_dace = pdf[-1]

    clip_etiqueta = detectar_area_util(pagina_etiqueta)
    clip_dace = detectar_area_util(pagina_dace)

    # aplica fator de escala apenas no clip
    clip_etiqueta = ampliar(clip_etiqueta, FATOR_ESCALA)
    clip_dace = ampliar(clip_dace, FATOR_ESCALA)

    nova = novo.new_page(
        width=LARGURA,
        height=ALTURA
    )

    metade = (ALTURA - ESPACO - MARGEM * 2) / 2

    area_superior = fitz.Rect(
        MARGEM,
        MARGEM,
        LARGURA - MARGEM,
        metade
    )

    area_inferior = fitz.Rect(
        MARGEM,
        metade + ESPACO,
        LARGURA - MARGEM,
        ALTURA - MARGEM
    )

    # ETIQUETA (rotacionada, sem manter proporção)
    nova.show_pdf_page(
        area_superior,
        pdf,
        pagina_etiqueta.number,
        clip=clip_etiqueta,
        rotate=90,
        keep_proportion=False
    )

    # DACE (rotacionada, sem manter proporção)
    nova.show_pdf_page(
        area_inferior,
        pdf,
        pagina_dace.number,
        clip=clip_dace,
        rotate=90,
        keep_proportion=False
    )

    saida = os.path.join(DESTINO, arquivo)

    novo.save(
        saida,
        garbage=4,
        deflate=True
    )

    novo.close()
    pdf.close()

    print(f"Gerado -> {arquivo}")

print("\nFinalizado!")
