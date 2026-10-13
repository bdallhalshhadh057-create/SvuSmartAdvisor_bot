import os
import telebot
import google.generativeai as genai
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. توكن تليغرام الحقيقي والكامل الخاص ببوتك
TELEGRAM_TOKEN = "8961690897:AAFRqw43Y1VBL0UkofqhPAxdwr9M9knEZp8"

# 2. قراءة مفتاح جيمناي من المتغير البيئي الآمن في سيرفر ريندر
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة الخدمات بالنسخ القياسية والمستقرة
genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
bot.remove_webhook()

# --- سيرفر فحص الحالة الوهمي لتخطي شروط منصة Render المجانية ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
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
        # التوجيه الحاكم المخصص لطلاب الحقوق في سوريا
        system_instruction = (
            "أنت مستشار ومساعد قانوني متخصص في مناهج الحقوق بالجامعة الافتراضية السورية. "
            "أجب بدقة متناهية بالاعتماد الحصري على القانون السوري واجتهادات محكمة النقض السورية. "
            "إذا طلب الطالب حل قضية أو وظيفة (Homework)، صغ الحل بأسلوب فريد وموزع منهجياً: "
            "(الوقائع، المشكلة القانونية، النص القانوني الواجب التطبيق، النتيجة والتعليل والأساس القانوني)."
        )
        
        # استدعاء النموذج فلاش السريع والمستقر والمجاني كلياً لعام 2026
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )
        response = model.generate_content(student_query)
        bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=waiting_msg.message_id)
    except Exception as e:
        error_msg = f"❌ حدث خطأ في الاتصال بالذكاء الاصطناعي.\nتفاصيل الخطأ: {str(e)}"
        bot.edit_message_text(error_msg, chat_id=message.chat.id, message_id=waiting_msg.message_id)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    print("🚀 مستشار SVU الذكي جاهز ومستقر تماماً...")
    bot.infinity_polling()
    
