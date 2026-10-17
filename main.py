import os
from flask import Flask, render_template, request, jsonify
import telebot
import google.generativeai as genai

# 1. إعدادات التوكن والذكاء الاصطناعي من كودك الأصلي
TELEGRAM_TOKEN = "8961690897:AAFRqw43Y1VBL0UkofqhPAxdwr9M9knEZp8"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تهيئة تطبيق Flask لإدارة واجهة الميني أب والموقع
app = Flask(__name__)

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

@app.route('/ask-gemini', methods=['POST'])
def ask_gemini_web():
    data = request.json
    subject = data.get('subject')
    task_type = data.get('task_type')
    input_text = data.get('input_text', '')

    if task_type == "summary":
        prompt = f"قدم تلخيصاً احترافياً وشرحاً مركزاً لأهم المحاور المتكررة في امتحانات مادة ({subject}) لطلاب الجامعة الافتراضية السورية."
    elif task_type == "quiz":
        prompt = f"قم بتوليد سؤال امتحاني مؤتمت واحد (خيارات متعددة) لمادة ({subject}) على نمط فحص SVU، مع 3 خيارات وتحديد الإجابة الصحيحة مع شرح التعليل القانوني السوري السليم."
    elif task_type == "homework":
        prompt = f"صغ حلاً قانونياً تفصيلياً فريداً ومبتكراً للوظيفة التالية في مادة ({subject}): '{input_text}' لحمايته من التشابه الجامعي وبأسلوب السلم الجامعي."

    try:
        model = genai.GenerativeModel(model_name='gemini-3.8-flash    , system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"})

# --- أقسام وعمليات البوت النصي التقليدي (Telebot) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في مستشار SVU الذكي!\n"
        "المساعد الافتراض الأول لطلاب الحقوق في الجامعة الافتراضية السورية.\n\n"
        "اضغط على زر 'افتح التطبيق' أسفل الشاشة لتجربة المنصة التفاعلية المتكاملة (ملخصات، امتحانات، حل وظائف فريدة)!"
    )
    bot.reply_to(message, welcome_text)

# إعداد مسار آمن مخصص لاستقبال رسائل البوت بدون أي تعارض (Webhook Endpoint)
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    # 1. إزالة أي ويب هوك قديم عالق يسبب التعارض بالخلفية
    bot.remove_webhook()
    
    # 2. جلب رابط السيرفر الخارجي تلقائياً وديناميكياً من بيئة Render لتفادي أخطاء الروابط اليدوية
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://onrender.com")
    
    # 3. ربط الويب هوك بالرابط الصحيح آلياً
    bot.set_webhook(url=render_url + "/" + TELEGRAM_TOKEN)
    print(f"🔗 [نجاح] تم ربط الويب هوك آلياً على الرابط: {render_url}")
    
    # 4. تشغيل سيرفر ويب Flask لخدمة الميني أب
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
