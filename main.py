import os
import json
import base64
from flask import Flask, render_template, request, jsonify
import telebot
import google.generativeai as genai
from google.genai import types

# 1. إعدادات التوكن والذكاء الاصطناعي
TELEGRAM_TOKEN = "8961690897:AAFRqw43Y1VBL0UkofqhPAxdwr9M9knEZp8"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask(__name__)

# التوجيه الحاكم الأساسي لضمان الالتزام بقوانين ومناهج SVU السورية
SYSTEM_INSTRUCTION = (
    "أنت مستشار ومساعد قانوني أكاديمي متخصص ومحترف في مناهج كلية الحقوق بالجامعة الافتراضية السورية (SVU). "
    "أجب بدقة متناهية بالاعتماد الحصري والكامل على نصوص التشريعات السورية واجتهادات محكمة النقض السورية المعمول بها. "
    "عند صياغة حلول الوظائف، احرص على تقديم أسلوب تحليل قانوني رصين ومتميز، مأصل فقهياً وقضائياً، "
    "وبصياغة فريدة ومبتكرة لكل طالب على حدة لضمان التفوق وحمايته التامة من أنظمة كشف التشابه (Plagiarism) في الجامعة ونيل علامة كاملة."
)

@app.route('/')
def index():
    return render_template('index.html')

# 1. مسار التلخيص والشرح التقليدي المعتمد
@app.route('/ask-gemini', methods=['POST'])
def ask_gemini_web():
    data = request.json
    subject = data.get('subject')
    prompt = f"قدم تلخيصاً احترافياً وشرحاً مركزاً لأهم المحاور والفقرات الامتحانية الرسمية المعتمدة في مادة ({subject}) لطلاب الجامعة الافتراضية السورية."
    
    try:
        model = genai.GenerativeModel(model_name='gemini-3.8-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 2. مسار الامتحان التفاعلي (يولد بيانات JSON مهيكلة للأزرار)
@app.route('/ask-quiz-interactive', methods=['POST'])
def ask_quiz_interactive():
    data = request.json
    subject = data.get('subject')
    
    # نطلب من جينماي إخراج البيانات بصيغة جيسون محددة جداً لتفهمها أزرار الموقع
    prompt = (
        f"قم بتوليد سؤال امتحاني مؤتمت واحد (خيارات متعددة) لمادة ({subject}) على نمط فحص SVU. "
        "يجب أن تكون الإجابة حصرياً بصيغة كائن JSON باللغة العربية دون أي نصوص إضافية خارج الأقواس، وبالمواصفات التالية:\n"
        "{\n"
        '  "question": "نص السؤال هنا",\n'
        '  "options": ["الخيار الأول", "الخيار الثاني", "الخيار الثالث"],\n'
        '  "correct": "اكتب هنا الخيار الصحيح حرفياً كما ورد في قائمة الخيارات",\n'
        '  "explanation": "الشرح والتعليل والأساس القانوني السوري للمادة"\n'
        "}"
    )
    
    try:
        model = genai.GenerativeModel(model_name='gemini-3.8-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"} # إجبار جينماي على صياغة JSON نقي
        )
        quiz_data = json.loads(response.text)
        return jsonify({"status": "success", "quiz_data": quiz_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 3. مسار حل الوظائف مع إرفاق وقراءة الملفات (الصور والـ PDF)
@app.route('/ask-homework-file', methods=['POST'])
def ask_homework_file():
    data = request.json
    subject = data.get('subject')
    question = data.get('question', '')
    file_data = data.get('file_data') # مصفوفة الـ Base64 القادمة من المتصفح
    
    prompt = f"صغ حلاً قانونياً تفصيلياً فريداً ومبتكراً للوظيفة التالية في مادة ({subject}): '{question}' بأسلوب السلم الجامعي لمنع التشابه."
    
    contents = [prompt]
    
    # إذا قام الطالب بإرفاق ملف، نقوم بتحويله وتمريره لـ Gemini ليقرأه
    if file_data and len(file_data) > 1:
        base64_string = file_data[1]
        mime_type = file_data[0].split(';')[0].split(':')[1]
        
        raw_file = base64.b64decode(base64_string)
        contents.append({
            'mime_type': mime_type,
            'data': raw_file
        })
        
    try:
        model = genai.GenerativeModel(model_name='gemini-3.8-flash', system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(contents)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- استقبال وتجهيز أوامر البوت النصي بشكل متوافق (Webhook) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في منصة مستشار SVU الذكي المتقدمة!\n\n"
        "اضغط على زر 'افتح التطبيق' أسفل الشاشة لتجربة المنصة الشجرية التفاعلية الجديدة (تقسيم السنوات، امتحانات تفاعلية، تحميل ملخصات PDF، وحل وظائف بالملفات المرفقة)!"
    )
    bot.reply_to(message, welcome_text)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://onrender.com")
    bot.set_webhook(url=render_url + "/" + TELEGRAM_TOKEN)
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
