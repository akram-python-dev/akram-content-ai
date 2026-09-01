import os
from flask import Flask, render_template, request, Response, jsonify
from google import genai
import json

app = Flask(__name__)

# استخدام مفتاح الـ API الخاص بنا لمعالجة طلبات المستخدمين بشكل فوري
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD-YOUR-FREE-INTEGRATION-KEY")
client = genai.Client(api_key=API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json(silent=True) or {}
        user_idea = data.get('idea', '')
        user_link = data.get('userLink', '')
        content_type = data.get('type', '')
        tone = data.get('tone', '')

        if not user_idea:
            return jsonify({'status': 'error', 'message': 'الرجاء كتابة الفكرة أولاً يا صديقي'}), 400

        # تجهيز نص التوجيه للرابط بدقة للتضمين البرمجي
        if user_link and user_link.strip():
            link_instruction = f"4. في نهاية الإعلان وتحديداً عند دعوة اتخاذ الإجراء (Call to Action)، ضع رابط العميل الحقيقي التالي بشكل مدمج وجذاب ليتواصل الناس معه من خلاله: {user_link}"
        else:
            link_instruction = "4. في نهاية الإعلان وتحديداً عند دعوة اتخاذ الإجراء (Call to Action)، ضع عبارة تسويقية عامة تطلب من الزبائن التواصل مباشرة مع صفحة المتجر."

        # بناء البرومبت الاحترافي وتعديل اسم المنصة ومنع الروابط النصية المربكة
        prompt = f"""
        أنت خبير تسويق رقمي وصانع محتوى محترف لصالح منصة "AkramFlow AI".
        بناءً على المدخلات التالية، قم بإنشاء محتوى عالي الجودة، غني بالتفاصيل ومقنع ومثير للاهتمام للجمهور فوراً:
        - الفكرة المستهدفة: {user_idea}
        - نوع العمل والمحتوى المطلوب: {content_type}
        - أسلوب ونبرة التخاطب: {tone}

        شروط الكتابة الصارمة:
        1. اكتب بلغة عربية فصحى جذابة وقوية وخالية تماماً من الأخطاء الإملائية.
        2. قسم المحتوى لفقرات احترافية تشمل: مقدمة تسويقية مشوقة، عناوين جانبية واضحة، ونقاط عملية.
        3. تحذير صارم: لا تكتب أقواس روابط فارغة أو نصوص مبهمة مثل "اضغط هنا للرابط"، بل استخدم الرابط الموفر فقط إن وُجد.
        {link_instruction}
        5. عند نهاية المحتوى بالكامل، قم بإضافة السطر التالي والمنفصل تماماً كعلامة مشفرة:
        [SHOW_CONTACT_BUTTON]
        6. اجعل الرد وافياً، مفصلاً، ومبتكراً بالكامل ليقدم قيمة حقيقية تدفع العميل للاستفادة والربح منها.
        """

        # تعديل لطلب النص كاملاً دفعة واحدة لإلغاء البطء والملل
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        
        generated_text = response.text if response.text else "لم يتمكن الذكاء الاصطناعي من إنشاء نص، حاول مجدداً."
        return Response(generated_text, mimetype='text/plain')

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'حدث خطأ في معالجة الذكاء الاصطناعي: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
