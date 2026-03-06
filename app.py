import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

PAYMENT_LINK = "https://TU_LINK_DE_PAGO"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🔥 Acceder al VIP de Jennifer", url=PAYMENT_LINK)]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
"""🔥 Hola, soy Jennifer

Bienvenido a mi chat privado 🔞

Escribe /VIP para acceder al contenido""",
        reply_markup=reply_markup
    )


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🔥 Acceder al VIP de Jennifer", url=PAYMENT_LINK)]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Pulsa el botón para desbloquear el VIP:",
        reply_markup=reply_markup
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", vip))

    print("BOT DE JENNIFER INICIADO")

    app.run_polling()


if __name__ == "__main__":
    main()
