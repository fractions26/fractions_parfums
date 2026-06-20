from PIL import Image

# 🔥 ARQUIVO ORIGINAL
entrada = r"C:\Users\wwwdl\OneDrive\Documentos\fractions_parfums\static\images\logo_nova.png"

# 🔥 ARQUIVO FINAL
saida = r"C:\Users\wwwdl\OneDrive\Documentos\fractions_parfums\static\images\favicon.ico"

with Image.open(entrada) as img:

    # ✅ RGB
    img = img.convert("RGB")

    # ✅ cria ICO com vários tamanhos
    img.save(
        saida,
        format="ICO",
        sizes=[
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256)
        ]
    )

print("✅ favicon.ico criado com múltiplos tamanhos!")