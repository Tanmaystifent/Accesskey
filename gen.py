from flask import Flask, request, jsonify
import time
import telebot

TOKEN = "7636549824:AAG_wYFWWF6folxLWQvkITq3leI1I5Vh-Xk"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Dictionary to store keys (key -> {expiry, max_devices, used})
ACCESS_KEYS = {}

# ✅ Generate Key via Telegram Bot (Admin Only)
@bot.message_handler(commands=['generate'])
def generate_key(message):
    if message.chat.id != 7929970637:  # Replace with your Telegram ID
        bot.reply_to(message, "❌ You are not authorized to generate keys!")
        return
    
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /generate <duration_in_sec> <max_devices>")
        return

    duration = int(parts[1])
    max_devices = int(parts[2])
    key = str(int(time.time()))

    ACCESS_KEYS[key] = {
        "expires": time.time() + duration,
        "max_devices": max_devices,
        "used": 0
    }
    
    bot.reply_to(message, f"✅ Key Generated!\n🔑 Key: `{key}`\n⏳ Valid for: {duration} sec\n📲 Max Devices: {max_devices}", parse_mode="Markdown")

# ✅ Validate Key via PowerShell Script
@app.route("/validate", methods=["POST"])
def validate_key():
    data = request.json
    key = data.get("key")

    if key not in ACCESS_KEYS:
        return jsonify({"valid": False, "error": "Invalid Key"}), 403

    info = ACCESS_KEYS[key]
    if time.time() > info["expires"]:
        del ACCESS_KEYS[key]
        return jsonify({"valid": False, "error": "Key Expired"}), 403

    if info["used"] >= info["max_devices"]:
        return jsonify({"valid": False, "error": "Device Limit Reached"}), 403

    ACCESS_KEYS[key]["used"] += 1
    return jsonify({"valid": True, "message": "Access Granted"})

# ✅ Start the Bot and Server
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=5000)
