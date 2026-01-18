from flask import Flask, request
from telegram import Bot, Update
import config

app = Flask(__name__)
bot = Bot(token=config.TELEGRAM_TOKEN)

@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    
    if update.message:  # Si llegó un mensaje
        chat_id = update.message.chat.id
        text = update.message.text or "¡Recibí tu mensaje!"
        bot.send_message(chat_id=chat_id, text=f"Eco: {text}")
    
    return "ok", 200

@app.route("/")
def index():
    return "Bot activo y listo", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

