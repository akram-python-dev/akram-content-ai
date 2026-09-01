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
            return jsonify({'status': 'error', 'message': 'الرجاء كتابة الفكرة أولاً'}), 400

        # صياغة رابط العميل بشكل خفيف ومباشر جداً لضمان السرعة
        link_text = f"\nرابط التواصل: {user_link}" if user_link and user_link.strip() else ""

        # برومبت مخفف وسريع للغاية ليعود الموقع طلقة كما كان
        prompt = f"""
        اكتب منشور تسويقي سريع ومقنع وجذاب جداً باللغة العربية حول هذه الفكرة: {user_idea}.
        نوع المحتوى المطلوب: {content_type}
        أسلوب ونبرة التخاطب: {tone}
        {link_text}
        
        اكتب سطر [SHOW_CONTACT_BUTTON] في نهاية الرد تماماً.
        """

        def generate_stream():
            try:
                response_stream = client.models.generate_content_stream(
                    model='gemini-3.6-flash',
                    contents=prompt,
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                yield f"error: {str(e)}"

        return Response(generate_stream(), mimetype='text/plain')

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'حدث خطأ: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
