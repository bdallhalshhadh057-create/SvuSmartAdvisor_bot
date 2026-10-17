import os
from flask import Flask, render_template, request, jsonify
import telebot
import google.generativeai as genai

# إعدادات التوكن والذكاء الاصطناعي
TELEGRAM_TOKEN = "8961690897:AAFRqw43Y1VBL0UkofqhPAxdwr9M9knEZp8"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تفعيل تطبيق Flask لإدارة واجهة الميني أب
app = Flask(__name__)

# التوجيه الحاكم الأساسي لـ Gemini
SYSTEM_INSTRUCTION = (
    "أنت مستشار ومساعد قانوني متخصص في مناهج الحقوق بالجامعة الافتراضية السورية (SVU). "
    "أجب بدقة متناهية بالاعتماد الحصري على القانون السوري واجتهادات محكمة النقض السورية. "
    "إذا طلب الطالب حل قضية أو وظيفة (Homework)، صغ الحل بأسلوب تفصيلي وأكاديمي فريد "
    "وموزع منهجياً لمنع أنظمة كشف التشابه ونيل علامة كاملة."
)

# --- مسارات الـ Mini App الواجهة ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask-gemini', methods=['POST'])
def ask_gemini_web():
    data = request.json
    subject = data.get('subject')
    task_type = data.get('task_type')
    input_text = data.get('input_text', '')

    if task_type == "summary":
        prompt = f"قدم تلخيصاً احترافياً وشرحاً مركزاً لأهم المحاور المتكررة في امتحانات مادة ({subject}) لطلاب الجامعة الافتراضية السورية."
    elif task_type == "quiz":
        prompt = f"قم بتوليد سؤال امتحاني مؤتمت واحد (خيارات متعددة) لمادة ({subject}) على نمط فحص SVU مع تحديد الإجابة الصحيحة وشرح التعليل القانوني السوري."
    elif task_type == "homework":
        prompt = f"صغ حلاً قانونياً تفصيلياً فريداً ومبتكراً للوظيفة التالية في مادة ({subject}): '{input_text}' لحمايته من التشابه الجامعي."

    try:
        model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- استقبال وتجهيز أوامر البوت النصي بشكل متوافق ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في مستشار SVU الذكي!\n\n"
        "اضغط على زر 'افتح التطبيق' أسفل الشاشة لتجربة المنصة التفاعلية المتكاملة (ملخصات، امتحانات، حل وظائف فريدة)!"
    )
    bot.reply_to(message, welcome_text)

# إعداد Webhook مخصص لاستقبال رسائل البوت بأمان بدون تعارض Polling
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    # إعداد وتأكيد اتصال البوت بالسيرفر لتجنب تعارض الـ getUpdates القديم
    bot.remove_webhook()
    # ضع هنا رابط السيرفر الفعلي الخاص بك المكتوب باللون الأزرق في صورتك
    bot.set_webhook(url="https://onrender.com" + TELEGRAM_TOKEN)
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
