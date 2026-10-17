import os
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import telebot
import google.generativeai as genai

# 1. إعدادات التوكن والذكاء الاصطناعي من كودك الأصلي
TELEGRAM_TOKEN = "8961690897:AAFRqw43Y1VBL0UkofqhPAxdwr9M9knEZp8"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
bot.remove_webhook()

# تهيئة تطبيق Flask لإدارة واجهة الميني أب والموقع
app = Flask(__name__)

# 2. قاعدة بيانات الاشتراكات المحمية (100 يوم وقفل على الـ Telegram ID)
SUBSCRIPTIONS = {
    "SVU-LAW-99X": {
        "expires_at": datetime.now() + timedelta(days=100),
        "bound_telegram_id": None
    },
    "SVU-VIP-777": {
        "expires_at": datetime.now() + timedelta(days=100),
        "bound_telegram_id": None
    }
}

# التوجيه الحاكم الأساسي لـ Gemini المتوافق مع مناهج الحقوق بـ SVU والقانون السوري
SYSTEM_INSTRUCTION = (
    "أنت مستشار ومساعد قانوني متخصص في مناهج الحقوق بالجامعة الافتراضية السورية (SVU). "
    "أجب بدقة متناهية بالاعتماد الحصري على القانون السوري واجتهادات محكمة النقض السورية. "
    "إذا طلب الطالب حل قضية أو وظيفة (Homework)، صغ الحل بأسلوب تفصيلي وأكاديمي فريد "
    "وموزع منهجياً: (الوقائع، المشكلة القانونية، النص القانوني الواجب التطبيق، النتيجة والتعليل والأساس القانوني) "
    "واحرص على أن تكون الصياغة فريدة ومبتكرة غير مكررة لحماية الطالب تماماً من أنظمة كشف التشابه ونيل علامة كاملة."
)

# --- أقسام وعمليات الـ Mini App (الموقع) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get('password')
    telegram_id = data.get('telegram_id')

    if password not in SUBSCRIPTIONS:
        return jsonify({"status": "error", "message": "⚠️ كود الاشتراك غير صحيح! تواصل مع الإدارة لشراء كود مفعّل."})
    
    sub = SUBSCRIPTIONS[password]
    
    if datetime.now() > sub["expires_at"]:
        return jsonify({"status": "error", "message": "❌ انتهت مدة اشتراكك (100 يوم). يرجى التجديد للاستمرار."})
    
    if sub["bound_telegram_id"] is not None and sub["bound_telegram_id"] != telegram_id:
        return jsonify({"status": "error", "message": "🚫 هذا الكود مفعّل مسبقاً على حساب تليجرام آخر! لا يمكن مشاركة الحسابات."})
    
    if sub["bound_telegram_id"] is None:
        sub["bound_telegram_id"] = telegram_id

    remaining_days = (sub["expires_at"] - datetime.now()).days
    return jsonify({"status": "success", "remaining_days": remaining_days})

@app.route('/ask-gemini', methods=['POST'])
def ask_gemini_web():
    data = request.json
    subject = data.get('subject')
    task_type = data.get('task_type')
    input_text = data.get('input_text', '')

    if task_type == "summary":
        prompt = f"قدم تلخيصاً احترافياً وشرحاً مركزاً لأهم المحاور المتكررة في امتحانات مادة ({subject}) لطلاب الجامعة الافتراضية."
    elif task_type == "quiz":
        prompt = f"قم بتوليد سؤال امتحاني مؤتمت واحد (خيارات متعددة) لمادة ({subject}) على نمط فحص SVU، مع 3 خيارات وتحديد الإجابة الصحيحة مع شرح التعليل القانوني السوري السليم."
    elif task_type == "homework":
        prompt = f"صغ حلاً قانونياً تفصيلياً فريداً ومبتكراً للوظيفة التالية في مادة ({subject}): '{input_text}'."

    try:
        model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"})


# --- أقسام وعمليات البوت النصي التقليدي (Telebot) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في مستشار SVU الذكي!\n"
        "المساعد الافتراضي الأول لطلاب الحقوق في الجامعة الافتراضية السورية.\n\n"
        "أرسل لي سؤالك القانوني الأول هنا، أو اضغط على زر 'افتح التطبيق' أسفل الشاشة لتجربة المنصة التفاعلية المتكاملة!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_law_queries(message):
    student_query = message.text
    waiting_msg = bot.reply_to(message, "⏳ جاري البحث في المراجع القانونية السورية وتحليل النص...")
    try:
        model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(student_query)
        bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=waiting_msg.message_id)
    except Exception as e:
        error_msg = f"❌ حدث خطأ في الاتصال بالذكاء الاصطناعي.\nتفاصيل الخطأ: {str(e)}"
        bot.edit_message_text(error_msg, chat_id=message.chat.id, message_id=waiting_msg.message_id)

# تشغيل البوت النصي في خيط (Thread) منفصل لكي لا يعطل موقع الويب
def run_telebot():
    print("🚀 البوت النصي يعمل الآن بالخلفية...")
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل خيط البوت
    bot_thread = threading.Thread(target=run_telebot, daemon=True)
    bot_thread.start()
    
    # تشغيل سيرفر ويب Flask الفعلي لخدمة الميني أب
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 سيرفر الميني أب يعمل على المنفذ: {port}")
    app.run(host="0.0.0.0", port=port)
        
