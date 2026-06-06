import discord
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# מאגר תקלות 0.83 (אפשר להוסיף ולערוך)
ERRORS_DB = {
    "error 38": "הפעל את המשחק כמנהל (Run as Administrator).",
    "2147467259": "זו בעיה מוכרת בהגדרות תצוגה, גש ל: https://discord.com/channels/1110273045706330202/1392212997191237662/1458044710714216581",
    "ijl15.dll": "חסר לך קובץ ה-DLL של המשחק. פתח טיקט ונישלח לך אותו."
}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text_to_analyze = message.content.lower()

    # סריקת תמונה וביצוע OCR אם צורפה אחת
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg']):
                try:
                    response = requests.get(attachment.url)
                    img = Image.open(BytesIO(response.content))
                    extracted_text = pytesseract.image_to_string(img).lower()
                    text_to_analyze += " " + extracted_text
                except Exception as e:
                    print(f"Error parsing image: {e}")

    if not text_to_analyze.strip():
        return

    # חיפוש תקלות מול המאגר
    for keyword, solution in ERRORS_DB.items():
        if keyword in text_to_analyze:
            await message.reply(f"**פתרון לתקלה:**\n{solution}")
            return
            
    # אם אין התאמה וזה נראה כמו בקשת תמיכה
    if "תקלה" in text_to_analyze or "error" in text_to_analyze or message.attachments:
        await message.reply("לא זיהיתי את התקלה הזו במאגר. אנא פתח טיקט להנהלה.")

# משיכת הטוקן ממשתני הסביבה בשרת
token = os.getenv('BOT_TOKEN')
if token:
    client.run(token)
else:
    print("Error: BOT_TOKEN environment variable not set.")
