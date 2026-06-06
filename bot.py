import discord
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import os
import re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# מאגר התקלות - שים לב לירידות השורה (\n) וללינקים של התמונות
ERRORS_DB = {
    "error 38": "הפעל את המשחק כמנהל (Run as Administrator).\nשלב 1: קליק ימני על האייקון.\nשלב 2: בחר Run as admin.\nhttps://i.imgur.com/example1.png",
    "2147467259": "האקשילד חוסם את ההפעלה.\nאנא כבה את האנטי-וירוס או הוסף את תיקיית המשחק ל-Exclusions.",
    "ijl15.dll": "חסר לך קובץ ה-DLL של המשחק.\nפתח טיקט ונישלח לך אותו."
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

    # 1. חיפוש תקלות מול המאגר
    for keyword, solution in ERRORS_DB.items():
        if keyword in text_to_analyze:
            await message.reply(f"**פתרון לתקלה:**\n{solution}")
            return
            
    # 2. אם אין התאמה במאגר: נבדוק אם המשתמש ניסה להזין מספר שגיאה מפורש
    # מחפש מילים כמו "error 123", "error123", או סתם רצף מספרים (2-5 ספרות)
    looks_like_error_code = re.search(r'(error\s*\d+|\b\d{2,5}\b)', text_to_analyze)
    
    if looks_like_error_code:
        await message.reply("אני לא מכיר את מספר השגיאה הזאת. אנא פתח טיקט להנהלה כדי לקבל עזרה פרטנית.")
        return

    # 3. אם אין מספר שגיאה ברור, וזה נראה כמו בקשת תמיכה כללית או תמונה לא ברורה
    if "תקלה" in text_to_analyze or "בעיה" in text_to_analyze or "error" in text_to_analyze or message.attachments:
        await message.reply("לא הצלחתי לזהות את התקלה מהתמונה או מהטקסט.\nאנא רשום את מספר השגיאה המדויק בצ'אט (למשל: `error 38`).")

# הרצת הבוט מול משתנה הסביבה ב-Railway
token = os.getenv('BOT_TOKEN')
if token:
    client.run(token)
else:
    print("Error: BOT_TOKEN environment variable not set.")
