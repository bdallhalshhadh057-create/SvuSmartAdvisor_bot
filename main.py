import telebot
from google import genai
from google.genai import types
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 🚨 ضع رموزك الرسمية هنا بدقة بين القوسين
TELEGRAM_TOKEN = "8961690897:AAEYjqBg6s97KWeaFQDDZvX1xHM7awZGYZk"
"
GEMINI_API_KEY = "AQ.Ab8RN6K2rPYDk2kdUFPuL5b5gmjnGbsdT6faXVSnVwC24WnWtw"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
bot.remove_webhook()

# --- الجزء الجديد: إنشاء سيرفر وهمي لخدعة منصة Render المجانية ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_health_server():
    # Render يرسل المنفذ تلقائياً عبر متغير بيئي اسمه PORT، وإذا لم يجده يستخدم 8080
    import os
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🚀 Health check server started on port {port}")
    server.serve_forever()
# -----------------------------------------------------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في مستشار SVU الذكي!\n"
        "المساعد الافتراضي الأول لطلاب الحقوق في الجامعة الافتراضية السورية.\n\n"
        "أرسل لي سؤالك القانوني الأول الآن وسأقوم بتحليله وفق القانون السوري!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_law_queries(message):
    student_query = message.text
    waiting_msg = bot.reply_to(message, "⏳ جاري البحث في المراجع القانونية السورية وتحليل النص...")
    try:
        system_instruction = (
            "أنت مستشار ومساعد قانوني متخصص في مناهج الحقوق بالجامعة الافتراضية السورية. "
            "أجب بدقة متناهية بالاعتماد الحصري على القانون السوري واجتهادات محكمة النقض السورية. "
            "إذا طلب الطالب حل قضية أو وظيفة (Homework)، صغ الحل بأسلوب فريد وموزع منهجياً: "
            "(الوقائع، المشكلة القانونية، النص القانوني الواجب التطبيق، النتيجة والتعليل والأساس القانوني)."
        )
        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=student_query,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.75)
        )
        bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=waiting_msg.message_id)
    except Exception as e:
        error_msg = f"❌ حدث خطأ في الاتصال.\nتفاصيل الخطأ: {str(e)}"
        bot.edit_message_text(error_msg, chat_id=message.chat.id, message_id=waiting_msg.message_id)

if __name__ == "__main__":
    # تشغيل السيرفر الوهمي في مسار منفصل ليرى Render أن الموقع يعمل بنجاح
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    
    # تشغيل البوت الأساسي لاستقبال الرسائل
    print("🚀 مستشار SVU الذكي مستعد الآن لاستقبال رسائل الطلاب...")
    bot.infinity_polling()
        
