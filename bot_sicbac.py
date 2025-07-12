import logging
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image
import io
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envie um print da estatística do Mega Sic Bac para análise.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    image_stream = io.BytesIO()
    await photo.download_to_memory(out=image_stream)
    image_stream.seek(0)

    image = Image.open(image_stream)
    text = pytesseract.image_to_string(image)

    result = analisar_resultado(text)
    await update.message.reply_text(result)

def analisar_resultado(texto):
    numeros = list(map(int, re.findall(r'\b\d{1,2}\b', texto)))

    analise = ""
    ultimos = numeros[-30:]  # últimos 30 resultados
    contador = {}

    for n in ultimos:
        contador[n] = contador.get(n, 0) + 1

    triplos = [k for k, v in contador.items() if v >= 3]
    duplos = [k for k, v in contador.items() if v == 2]
    quadras = [k for k, v in contador.items() if v >= 4]

    if quadras:
        analise += f"🔴 Quadra(s): {quadras}\n"
    if triplos:
        analise += f"🟡 Triplo(s): {triplos}\n"
    if duplos:
        analise += f"🟢 Duplo(s): {duplos}\n"

    if not analise:
        analise = "Nenhum padrão claro encontrado.\n"

    return "📊 Análise de padrões Mega Sic Bac:\n" + analise

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()
