import telebot
from google import genai
from google.genai import types

# 🚨 ضع رموزك الرسمية والجديدة هنا بدقة بين القوسين
TELEGRAM_TOKEN = "8961690897:AAEYjqBg6s97KWeaFQDDZvX1xHM7awZGYZk"
GEMINI_API_KEY = "AQ.Ab8RN6K2rPYDk2kdUFPuL5b5gmjnGbsdT6faXVSnVwC24WnWtw"

# تهيئة البوت ومحرك الذكاء الاصطناعي
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# فصل البوت عن أي ارتباطات سابقة ليعمل من الصفر بنقاء
bot.remove_webhook()

# رسالة الترحيب عند الضغط على /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚖️ مرحباً بك في مستشار SVU الذكي!\n"
        "المساعد الافتراضي الأول لطلاب الحقوق في الجامعة الافتراضية السورية.\n\n"
        "أنا هنا لخدمتك في:\n"
        "📑 تلخيص المقررات بدقة علمية.\n"
        "📝 حل وظائف المقررات وقضاياها بشكل فريد وغير مكرر.\n"
        "🎯 توليد اختبارات أتمتة تحاكي امتحانات الجامعة.\n\n"
        "أرسل لي سؤالك القانوني الأول الآن وسأقوم بتحليله وفق القانون السوري!"
    )
    bot.reply_to(message, welcome_text)

# استقبال رسائل الطلاب ومعالجتها عبر جيمناي
@bot.message_handler(func=lambda message: True)
def handle_law_queries(message):
    student_query = message.text
    
    # إرسال رسالة انتظار مريحة للطالب
    waiting_msg = bot.reply_to(message, "⏳ جاري البحث في المراجع القانونية السورية وتحليل النص...")

    try:
        # التوجيه الحاكم المخصص للحقوق في سوريا
        system_instruction = (
            "أنت مستشار ومساعد قانوني متخصص في مناهج الحقوق بالجامعة الافتراضية السورية. "
            "أجب بدقة متناهية بالاعتماد الحصري على القانون السوري واجتهادات محكمة النقض السورية. "
            "إذا طلب الطالب حل قضية أو وظيفة (Homework)، صغ الحل بأسلوب فريد وموزع منهجياً: "
            "(الوقائع، المشكلة القانونية، النص القانوني الواجب التطبيق، النتيجة والتعليل والأساس القانوني). "
            "نوع دائماً في الصياغة اللغوية والكلمات لتجنب تشابه الحلول بين الطلاب بشكل قطعي."
        )

        # استدعاء نموذج جيمناي السريع والمجاني 1.5 Flash
        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=student_query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.75 # درجة إبداع تضمن فرادة صياغة الوظائف لكل طالب
            )
        )
        
        # استبدال رسالة الانتظار بالرد النهائي الصادر من جيمناي
        bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=waiting_msg.message_id)

    except Exception as e:
        error_msg = f"❌ حدث خطأ في الاتصال. تأكد من تشغيل البروكسي أو الـ VPN الخاص بك داخل سوريا.\nتفاصيل الخطأ: {str(e)}"
        bot.edit_message_text(error_msg, chat_id=message.chat.id, message_id=waiting_msg.message_id)

# بدء تشغيل البوت واستماع الرسائل
print("🚀 مستشار SVU الذكي يعمل الآن بنجاح ومستعد لاستقبال رسائل الطلاب...")
bot.infinity_polling()
