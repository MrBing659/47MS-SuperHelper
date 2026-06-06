import discord
from discord.ui import Button, View
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import os
import re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ==========================================
# מאגר התקלות שלך - כאן תדביק את השורות שאני מכין לך
# ==========================================
ERRORS_DB = {
    "2147467259": "**error code: -2147467259 (unspecified error)**\n**מהות השגיאה:**\nמשהו שקשור להגדרות \\ שינוי גראפיקה \\ דיירקט-איקס.\n\n**פתרון 1:**\nDisplay Settings -> Advanced Display Settings -> Display Adapter Properties -> Select the 'Monitor' tab -> and change the screen refresh rate from 59Hz to 60Hz and press Apply.\n\n**פתרון 2:**\nיש ללחוץ על WinKey + R במקלדת,\nואז לרשום Regedit ולגשת לנתיב:\n`HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Wizet\\MapleStory`\nיש למחוק את התיקייה MapleStory.\nזה יאפס את הגדרות התצוגה לברירת מחדל.",
    "vcruntime140": "**שגיאה: VCRUNTIME140.dll / MSVCP140.dll Missing**\n**מהות השגיאה:**\nמחסור בקובץ.\n\n**פתרון:**\nיש להתקין Microsoft Visual C++ Redistributable.\nנא להיכנס לפה ולהוריד את הגרסה העדכנית:\nhttps://learn.microsoft.com/en-us/answers/questions/4269238/vcruntime140-dll-and-msvcp140-dll-missing-in-windo",
    "msvcp140": "**שגיאה: VCRUNTIME140.dll / MSVCP140.dll Missing**\n**מהות השגיאה:**\nמחסור בקובץ.\n\n**פתרון:**\nיש להתקין Microsoft Visual C++ Redistributable.\nנא להיכנס לפה ולהוריד את הגרסה העדכנית:\nhttps://learn.microsoft.com/en-us/answers/questions/4269238/vcruntime140-dll-and-msvcp140-dll-missing-in-windo",
    "desktop runtime missing": "**שגיאה: .NET Desktop Runtime Missing**\n**מהות השגיאה:**\nמחסור בקבצים.\n\n**פתרון:**\nבשגיאה שקופצת, לחצו על \"Download It Now\" ותתקינו.",
    "missing a few files": "**שגיאה: You appear to be missing a few files needed to run the game**\n**מהות השגיאה:**\nמחסור בקבצי משחק.\n\n**פתרון:**\nהפעלה מחדש למחשב ולהריץ לאנצ'ר מחדש.",
    "2147467261": "**error code: -2147467261 (Invalid Pointer)**\n**מהות השגיאה:**\nשגיאה באתחול בקבצי המשחק.\n\n**פתרון:**\nהפעלה מחדש למחשב ולהריץ לאנצ'ר מחדש.",
    "freezes": "**שגיאה: קליינט קורס \\ קופא (Game Instability / Freezes / Crashes)**\n**מהות התקלה:**\nבעיה בתאימות הקליינט.\n\n**פתרון:**\nיש לבצע פעולה זו גם ל-Launcher.exe וגם ל-FortySevenMS.exe !!\n1. לחצן ימני על הקובץ.\n2. בחרו ב-Properties (או Options).\n3. עברו ללשונית Compatibility.\n4. סמנו את Run this program in compatibility mode.\n5. בחרו ב-Windows 7.\n6. סמנו את Run this program as administrator.\n7. לחצו על \"Apply\" ואז \"Ok\".\n8. הפעילו את המשחק דרך הלאנצ'ר.",
    "crashes": "**שגיאה: קליינט קורס \\ קופא (Game Instability / Freezes / Crashes)**\n**מהות התקלה:**\nבעיה בתאימות הקליינט.\n\n**פתרון:**\nיש לבצע פעולה זו גם ל-Launcher.exe וגם ל-FortySevenMS.exe !!\n1. לחצן ימני על הקובץ.\n2. בחרו ב-Properties (או Options).\n3. עברו ללשונית Compatibility.\n4. סמנו את Run this program in compatibility mode.\n5. בחרו ב-Windows 7.\n6. סמנו את Run this program as administrator.\n7. לחצו על \"Apply\" ואז \"Ok\".\n8. הפעילו את המשחק דרך הלאנצ'ר.",
    "קורס": "**שגיאה: קליינט קורס \\ קופא (Game Instability / Freezes / Crashes)**\n**מהות התקלה:**\nבעיה בתאימות הקליינט.\n\n**פתרון:**\nיש לבצע פעולה זו גם ל-Launcher.exe וגם ל-FortySevenMS.exe !!\n1. לחצן ימני על הקובץ.\n2. בחרו ב-Properties (או Options).\n3. עברו ללשונית Compatibility.\n4. סמנו את Run this program in compatibility mode.\n5. בחרו ב-Windows 7.\n6. סמנו את Run this program as administrator.\n7. לחצו על \"Apply\" ואז \"Ok\".\n8. הפעילו את המשחק דרך הלאנצ'ר.",
    "קופא": "**שגיאה: קליינט קורס \\ קופא (Game Instability / Freezes / Crashes)**\n**מהות התקלה:**\nבעיה בתאימות הקליינט.\n\n**פתרון:**\nיש לבצע פעולה זו גם ל-Launcher.exe וגם ל-FortySevenMS.exe !!\n1. לחצן ימני על הקובץ.\n2. בחרו ב-Properties (או Options).\n3. עברו ללשונית Compatibility.\n4. סמנו את Run this program in compatibility mode.\n5. בחרו ב-Windows 7.\n6. סמנו את Run this program as administrator.\n7. לחצו על \"Apply\" ואז \"Ok\".\n8. הפעילו את המשחק דרך הלאנצ'ר.",
    "closes without starting": "**שגיאה: הלאנצ'ר נפתח ואז נסגר והמשחק לא עולה**\n**מהות התקלה:**\nשגיאה באחד מקבצי המערכת.\n\n**פתרון:**\nכנסו לקישור, תורידו ותתקינו את הקובץ:\nhttps://aka.ms/vs/17/release/vc_redist.x86.exe",
    "הלאנצ'ר נפתח ואז נסגר": "**שגיאה: הלאנצ'ר נפתח ואז נסגר והמשחק לא עולה**\n**מהות התקלה:**\nשגיאה באחד מקבצי המערכת.\n\n**פתרון:**\nכנסו לקישור, תורידו ותתקינו את הקובץ:\nhttps://aka.ms/vs/17/release/vc_redist.x86.exe",
    "missing or corrupted": "**שגיאה: Errors saying the client is missing or corrupted**\n**מהות התקלה:**\nהאנטיוירוס מחק משהו מהתיקייה.\n\n**פתרון:**\nצפו בסרטון ותחריגו את תיקיית המשחק באנטי-וירוס:\nhttps://discord.com/channels/1110273045706330202/1265612585093562368",
    "httpclient timeout": "**שגיאה: Cannot Connect to Server (HttpClient Timeout)**\n**מהות התקלה:**\nאין חיבור ביניכם לבין השרת של הלאנצ'ר.\n\n**בדיקה לפני פתרון:**\n1. כנסו ל: https://gamefile.fortysevenms.online/update/\n2. אם אתם רואים שם מלא טקסט שמתחיל ב-\"New Patch\" - תפתחו טיקט. (https://discord.com/channels/1110273045706330202/1110639484938227712)\n3. אם העמוד לא טוען - יש לכם ככל הנראה בעיה בספקית האינטרנט שלכם.\n\n**פתרון זמני:**\nנסו להתחבר מהאינטרנט של הנייד שלכם (שלא יהיה מחובר ל-Wifi).\n\n**פתרון קבוע 1:**\nלהתקשר לספקית האינטרנט ולבקש לבטל את ה-Cyber Guard.\n\n**פתרונות קבועים נוספים (שינוי DNS):**\n**הדרך הקלה (הורדת תוכנה):**\n1. כנסו, תורידו ותתקינו את https://one.one.one.one/\n2. בתוכנות הפתוחות ברקע (ליד השעון) יהיה לכם אייקון של ענן בצבע כתום, לחצו עליו ואז על הפעלה.\n3. נסו להתחבר למשחק.",
}

# ==========================================
# הגדרת הכפתורים (UI Views)
# ==========================================

# 3. כפתור לינק לפתיחת טיקט (קופץ כשלוחצים "התקלה לא נפתרה")
class TicketView(View):
    def __init__(self):
        super().__init__()
        # כפתור מסוג URL שמפנה ישירות ללינק שביקשת
        self.add_item(Button(label="פתח טיקט תמיכה", url="https://discord.com/channels/1110273045706330202/1110639484938227712", style=discord.ButtonStyle.link, emoji="🎫"))

# 2. תפריט "לא עזר לי"
class NoHelpView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="התקלה לא נפתרה", style=discord.ButtonStyle.secondary, emoji="🛠️")
    async def not_resolved(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("הבנתי. אל תשבור את המקלדת עדיין.\nלחץ על הכפתור למטה כדי לפתוח טיקט והצוות שלנו יתחבר לעזור לך באופן פרטני.", view=TicketView(), ephemeral=True)

    @discord.ui.button(label="יש לי תקלה חדשה", style=discord.ButtonStyle.primary, emoji="🆕")
    async def new_issue(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("שגר. תעלה לפה צילום מסך ברור של השגיאה או תרשום את המספר המדויק שלה.", ephemeral=True)

# 1. תפריט ראשי "האם עזר?" (מצורף לכל פתרון שהבוט שולח)
class SolutionView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="כן", style=discord.ButtonStyle.success, emoji="✅")
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("שמחתי לעזור! תן בראש במשחק.\n**- SuperHelper** 🦸‍♂️", ephemeral=True)

    @discord.ui.button(label="לא", style=discord.ButtonStyle.danger, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("באסה. מה הלאה?", view=NoHelpView(), ephemeral=True)


# ==========================================
# לוגיקת הבוט המרכזית
# ==========================================

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text_to_analyze = message.content.lower()

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'webp']):
                try:
                    response = requests.get(attachment.url)
                    img = Image.open(BytesIO(response.content))
                    
                    img = img.convert('L')
                    img = img.resize((img.width * 3, img.height * 3), Image.Resampling.LANCZOS)
                    
                    extracted_text = pytesseract.image_to_string(img).lower()
                    text_to_analyze += " " + extracted_text
                except Exception as e:
                    print(f"Error parsing image: {e}")
                    await message.reply(f"**תקלת מערכת (OCR קורס):**\n`{e}`")

    if not text_to_analyze.strip():
        return

    # חיפוש במאגר
    for keyword, solution in ERRORS_DB.items():
        if keyword in text_to_analyze:
            # הוספנו פה את ה-SolutionView (הכפתורים) שיוצמדו להודעה
            await message.reply(f"**פתרון לתקלה:**\n{solution}\n\n**האם הפתרון עזר לך?**", view=SolutionView())
            return
            
    looks_like_error_code = re.search(r'(error\s*\d+|\b\d{2,15}\b)', text_to_analyze)
    
    if looks_like_error_code:
        await message.reply("אני לא מכיר את מספר השגיאה הזאת. אנא פתח טיקט להנהלה כדי לקבל עזרה פרטנית.", view=TicketView())
        return

    if "תקלה" in text_to_analyze or "בעיה" in text_to_analyze or "error" in text_to_analyze or message.attachments:
        await message.reply("לא הצלחתי לזהות את התקלה מהתמונה או מהטקסט.\nאנא רשום את מספר השגיאה המדויק בצ'אט (למשל: `error 38`).")

token = os.getenv('BOT_TOKEN')
if token:
    client.run(token)
else:
    print("Error: BOT_TOKEN environment variable not set.")
