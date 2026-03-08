import os
import stripe
from flask import Flask, request
from telegram import Bot
from database import init_db, add_or_update_user, is_user_active

BOT_TOKEN = os.getenv("BOT_TOKEN")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")
ENDPOINT_SECRET = os.getenv("ENDPOINT_SECRET")
GROUP_ID = int(os.getenv("GROUP_ID"))
VIP_DAYS = int(os.getenv("VIP_DAYS", 30))

stripe.api_key = STRIPE_SECRET
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

init_db()


@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            ENDPOINT_SECRET
        )
    except Exception:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]
        telegram_id = session["metadata"].get("telegram_id")

        if not telegram_id:
            return "", 200

        if is_user_active(telegram_id):
            return "", 200

        add_or_update_user(telegram_id, VIP_DAYS)

        try:
            invite_link = bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                member_limit=1
            )

            bot.send_message(
                chat_id=telegram_id,
                text=f"💎 Payment successful!\n\nVIP Access:\n{invite_link.invite_link}"
            )

        except Exception:
            pass

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
