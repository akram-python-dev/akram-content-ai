import os
from flask import Flask, render_template, request, Response, jsonify
from google import genai
import json

app = Flask(__name__)

# استخدام مفتاح الـ API الخاص بنا لمعالجة طلبات المستخدمين بشكل فوري وحي
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD-YOUR-FREE-INTEGRATION-KEY")
client = genai.Client(api_key=API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        user_idea = data.get('idea', '')
        content_type = data.get('type', 'مقالة')
        tone = data.get('tone', 'إبداعي')

        if not user_idea:
            return jsonify({'status': 'error', 'message': 'الرجاء كتابة الفكرة أولاً يا صديقي!'}), 400

        # بناء البرومبت الاحترافي الذي يضمن ردوداً غنية ووافية وطويلة للعميل
        prompt = f"""
        أنت خبير تسويق رقمي وصانع محتوى محترف تعمل لصالح منصة "ذكاء أكرم - Akram AI". 
        بناءً على المدخلات التالية، قم بإنشاء محتوى عالي الجودة، غني بالتفاصيل، ومقنع وجاهز للاستخدام التجاري فوراً:
        - الفكرة المستهدفة: {user_idea}
        - نوع العمل والمحتوى المطلوب: {content_type}
        - أسلوب ونبرة التخاطب: {tone}
        
        شروط الكتابة الصارمة:
        1. اكتب بلغة عربية فصحى جذابة وقوية وخالية تماماً من الأخطاء السطحية.
        2. قسّم المحتوى لفقرات احترافية تشمل: مقدمة تسويقية مشوقة، عناوين جانبية واضحة، نقاط عملية، وخاتمة قوية بها دعوة واضحة لاتخاذ إجراء (Call to Action).
        3. اجعل الرد وافياً، مفصلاً، ومبتكراً بالكامل ليقدم قيمة حقيقية تدفع العميل للاستفادة والربح منها.
        """

        # استخدام البث المباشر (Stream) لتفادي انقطاع الاتصال (Timeout) في سيرفر Render المجاني
        def generate_stream():
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            full_text = ""
            for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text
            
            # إرسال النتيجة النهائية بتنسيق JSON متوافق مع واجهتك الحالية
            yield json.dumps({'status': 'success', 'content': full_text})

        return Response(generate_stream(), mimetype='application/json')

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'حدث خطأ في معالجة الذكاء الاصطناعي: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
  
