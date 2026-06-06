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

# מאגר התקלות המעודכן
ERRORS_DB = {
    "2147467259": "error code: -2147467259 (unspecified error) /n מהות השגיאה:/n משהו שקשור להגדרות \ שינוי גראפיקה \ דיירקט-איקס/n פתרון:/n Display Settings -> Advanced Display Settings -> Display Adapter Properties -> Select the "Monitor" tab -> and change the screen refresh rate from 59Hz to 60Hz and press Apply. /n פתרון אפשרי:/n יש לפתוח  Regedit /n לגשת לנתיב /n HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Wizet\MapleStory /n למחוק את התיקייה /n MapleStory \n זה יאפס את הגדרות התצוגה לברירת מחדל.",
    "error 38": "הפעל את המשחק כמנהל (Run as Administrator).\nשלב 1: קליק ימני על האייקון.\nשלב 2: בחר Run as admin.",
    "hackshield": "האקשילד חוסם את ההפעלה.\nאנא כבה את האנטי-וירוס או הוסף את תיקיית המשחק ל-Exclusions.",
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
            # הוספנו webp למקרה שדיסקורד ממיר את ההדבקה
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'webp']):
                try:
                    response = requests.get(attachment.url)
                    img = Image.open(BytesIO(response.content))
                    
                    # ה"משקפיים" של ה-OCR: הפיכה לשחור-לבן והגדלה פי 3 כדי לזהות פונט פיקסל-ארט של מייפל
                    img = img.convert('L')
                    img = img.resize((img.width * 3, img.height * 3), Image.Resampling.LANCZOS)
                    
                    extracted_text = pytesseract.image_to_string(img).lower()
                    print(f"DEBUG OCR TEXT: {extracted_text}") # מדפיס ללוגים ב-Railway כדי שתוכל לעקוב
                    
                    text_to_analyze += " " + extracted_text
                except Exception as e:
                    print(f"Error parsing image: {e}")
                    # אם השרת לא מצא את ה-Tesseract, הבוט יצעק עליך בדיסקורד ולא ישתוק
                    await message.reply(f"**תקלת מערכת (OCR קורס):**\n`{e}`\nתבדוק אם קובץ ה-apt.txt הותקן כמו שצריך ב-Railway.")

    if not text_to_analyze.strip():
        return

    # 1. חיפוש תקלות מול המאגר
    for keyword, solution in ERRORS_DB.items():
        if keyword in text_to_analyze:
            await message.reply(f"**פתרון לתקלה:**\n{solution}")
            return
            
    # 2. זיהוי מספר שגיאה מפורש (מאפשר עכשיו מספרי שגיאה ארוכים של עד 15 ספרות)
    looks_like_error_code = re.search(r'(error\s*\d+|\b\d{2,15}\b)', text_to_analyze)
    
    if looks_like_error_code:
        await message.reply("אני לא מכיר את מספר השגיאה הזאת. אנא פתח טיקט להנהלה כדי לקבל עזרה פרטנית.")
        return

    # 3. אם אין מספר שגיאה ברור ואין התאמה במאגר
    if "תקלה" in text_to_analyze or "בעיה" in text_to_analyze or "error" in text_to_analyze or message.attachments:
        await message.reply("לא הצלחתי לזהות את התקלה מהתמונה או מהטקסט.\nאנא רשום את מספר השגיאה המדויק בצ'אט (למשל: `error 38`).")

# משיכת הטוקן מהשרת
token = os.getenv('BOT_TOKEN')
if token:
    client.run(token)
else:
    print("Error: BOT_TOKEN environment variable not set.")
