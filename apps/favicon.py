from PIL import Image

entrada = r"C:\Users\wwwdl\OneDrive\Documentos\fractions_parfums\static\images\favicon.png"
saida = r"C:\Users\wwwdl\OneDrive\Documentos\fractions_parfums\static\images\favicon.png"

with Image.open(entrada) as img:

    img = img.convert("RGBA")

    # Recomendo 512x512
    img = img.resize((512, 512))

    img.save(saida, format="PNG", optimize=True)

print("✅ favicon.png atualizado")