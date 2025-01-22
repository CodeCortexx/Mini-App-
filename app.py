import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import openai

# Lade Umgebungsvariablen
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Logging einrichten
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Speicher für generierte Bilder
community_gallery = []

# Start-Befehl
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Willkommen! Sende mir eine Beschreibung, und ich werde ein KI-generiertes Bild erstellen. "
        "Du kannst auch die /gallery Funktion verwenden, um Bilder der Community zu erkunden."
    )

# Bildgenerierung
def generate_image(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    update.message.reply_text("Einen Moment, ich generiere dein Bild...")

    try:
        # Bild mit OpenAI DALL·E generieren
        response = openai.Image.create(
            prompt=user_input,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']

        # Bild zur Community-Galerie hinzufügen
        community_gallery.append({"prompt": user_input, "url": image_url})

        # Bild senden
        update.message.reply_photo(photo=image_url, caption=f"Beschreibung: {user_input}")
    except Exception as e:
        logger.error(f"Fehler bei der Bildgenerierung: {e}")
        update.message.reply_text("Entschuldigung, es gab ein Problem bei der Generierung deines Bildes.")

# Galerie durchsuchen
def gallery(update: Update, context: CallbackContext) -> None:
    if not community_gallery:
        update.message.reply_text("Die Galerie ist noch leer. Erstelle ein Bild mit einer Beschreibung!")
        return

    # Inline-Tastatur mit Bildern erstellen
    keyboard = [
        [InlineKeyboardButton(f"Bild {i+1}: {item['prompt'][:20]}...", callback_data=str(i))]
        for i, item in enumerate(community_gallery)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Wähle ein Bild aus der Galerie:", reply_markup=reply_markup)

# Callback für Galerie-Auswahl
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Bild basierend auf Auswahl senden
    index = int(query.data)
    selected_image = community_gallery[index]
    query.edit_message_text(text=f"Beschreibung: {selected_image['prompt']}")
    context.bot.send_photo(chat_id=query.message.chat_id, photo=selected_image['url'])

# Fehlerbehandlung
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} hat einen Fehler verursacht: {context.error}")

# Hauptfunktion
def main() -> None:
    """Startet den Bot."""
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Befehle und Handler registrieren
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("gallery", gallery))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_image))
    dispatcher.add_error_handler(error)

    # Bot starten
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
