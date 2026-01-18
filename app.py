from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import config
import stripe
import os
import sqlite3
app = Flask(__name__)

bot = Bot(token=config.TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

from datetime import datetime, timedelta

# --- Setup ---
app = Flask(__name__)
bot = Bot(token=config.TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)
stripe.api_key = config.STRIPE_KEY

# --- Base de datos ---
DB_PATH = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        model TEXT,
        plan TEXT,
        subscription_end TEXT,
        payment_id TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# --- Handlers ---
def start(update, context):
    update.message.reply_text(
        "Si quieres ver contenido exclusivo haz /VIP"
    )

def vip(update, context):
    user_id = update.message.from_user.id
    args = context.args
    if not args:
        update.message.reply_text(
            "Debes indicar el modelo: /VIP A o /VIP B"
        )
        return
    model_name = args[0].upper()
    if model_name not in config.MODELS:
        update.message.reply_text("Modelo inválido. Usa A o B.")
        return

    model = config.MODELS[model_name]

    # Crear sesión Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': model["stripe_price_id"],
            'quantity': 1
        }],
        mode='payment',
        success_url=config.WEBHOOK_URL,
        cancel_url=config.WEBHOOK_URL,
        metadata={'user_id': user_id, 'model': model_name}
    )

    # Respuesta camuflada
    update.message.reply_text(
        f"Accede al canal VIP pinchando [AQUI]({session.url})",
        parse_mode="Markdown"
    )

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("VIP", vip))

# --- Webhook Stripe ---
@app.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return str(e), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['metadata']['user_id'])
        model_name = session['metadata']['model']
        vip_chat = config.MODELS[model_name]["vip_channel_id"]

        # Añadir usuario al VIP
        try:
            bot.invite_chat_member(vip_chat, user_id)
        except Exception as e:
            print(f"No se pudo añadir {user_id} al VIP: {e}")

        # Guardar en DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        sub_end = datetime.utcnow() + timedelta(days=30)
        c.execute("""INSERT OR REPLACE INTO users
                     (user_id, model, plan, subscription_end, payment_id)
                     VALUES (?, ?, ?, ?, ?)""",
                  (user_id, model_name, "vip", sub_end.isoformat(), session['id']))
        conn.commit()
        conn.close()

    return jsonify(success=True)

# --- Expiraciones ---
def check_expirations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("SELECT user_id, model, subscription_end FROM users WHERE plan='vip'")
    rows = c.fetchall()
    for user_id, model_name, sub_end in rows:
        if sub_end < now:
            vip_chat = config.MODELS[model_name]["vip_channel_id"]
            try:
                bot.kick_chat_member(vip_chat, user_id)
            except:
                pass
            c.execute("UPDATE users SET plan='expired' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# --- Webhook Telegram ---
@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    # Revisar expiraciones en cada mensaje (para pruebas locales)
    check_expirations()
    return "ok", 200

@app.route("/")
def index():
    return "Bot Tiffany funcionando 🚀", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

