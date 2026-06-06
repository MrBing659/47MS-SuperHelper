# גרסת פייתון קלה ומהירה
FROM python:3.11-slim

# התקנת מנוע ה-OCR ברמת מערכת ההפעלה
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng && \
    apt-get clean

# הגדרת תיקיית עבודה
WORKDIR /app

# העתקת קבצי הדרישות והתקנתם
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת שאר הקוד
COPY . .

# הפעלת הבוט
CMD ["python", "bot.py"]
