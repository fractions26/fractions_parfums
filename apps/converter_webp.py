import os
from PIL import Image

# 🔥 CAMINHO DA SUA PASTA
PASTA = r"C:\Users\G0012073\OneDrive - Telefonica\Documents\fractions_parfums\fractions_parfums\media\perfumes\descricao"

# ✅ QUALIDADE (80-85 ideal)
QUALIDADE = 85

def converter_png_para_webp():
    total = 0
    convertidos = 0
    ignorados = 0
    erros = 0

    for arquivo in os.listdir(PASTA):
        if arquivo.lower().endswith(".jfif"):

            total += 1

            caminho_arquivo = os.path.join(PASTA, arquivo)
            novo_nome = arquivo.rsplit(".", 1)[0] + ".webp"
            caminho_novo = os.path.join(PASTA, novo_nome)

            # ✅ Evita reconverter se já existir
            if os.path.exists(caminho_novo):
                print(f"⏭️ Já existe: {novo_nome}")
                ignorados += 1
                continue

            try:
                # ✅ Usa contexto e mantém modo original (corrige o problema monocromático)
                with Image.open(caminho_arquivo) as img:

                    img.save(
                        caminho_novo,
                        "WEBP",
                        quality=QUALIDADE,
                        method=6  # 🔥 melhor compressão WEBP
                    )

                print(f"✅ Convertido: {arquivo} → {novo_nome}")
                convertidos += 1

            except Exception as e:
                print(f"❌ Erro em {arquivo}: {e}")
                erros += 1

    # 📊 Resumo final
    print("\n📊 RESUMO:")
    print(f"Arquivos encontrados: {total}")
    print(f"Convertidos: {convertidos}")
    print(f"Ignorados (já existiam): {ignorados}")
    print(f"Erros: {erros}")


if __name__ == "__main__":
    converter_png_para_webp()