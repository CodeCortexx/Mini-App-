import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# OpenAI API-Key (DALL-E)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram-Bot-Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setze OpenAI API-Key
openai.api_key = OPENAI_API_KEY

# Funktion, die das Bild generiert
def generate_ai_art(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        return f"Fehler bei der Generierung des Bildes: {e}"

# Start-Befehl
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Willkommen zur AI Art Generator App! "
        "Sende einfach eine Beschreibung, und ich generiere ein Kunstwerk für dich."
    )

# Handler für die Eingabe des Nutzers
def handle_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    update.message.reply_text("Bitte warte, dein Bild wird generiert...")
    
    # Bild generieren
    image_url = generate_ai_art(prompt)
    if "Fehler" in image_url:
        update.message.reply_text(image_url)
    else:
        update.message.reply_photo(photo=image_url, caption="Hier ist dein AI-generiertes Kunstwerk!")

# Main-Funktion
def main():
    # Telegram-Bot initialisieren
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Befehle und Nachrichtenhandler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Bot starten
    updater.start_polling()
    print("Bot läuft...")
    updater.idle()

if __name__ == "__main__":
    main()
