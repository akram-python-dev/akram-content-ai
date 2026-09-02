import os
from flask import Flask, render_template, request, Response, jsonify
from google import genai
import json

app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# إعدادات قاعدة البيانات
app.config['SECRET_KEY'] = 'AkramFlowSuperSecretKey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# إعداد نظام إدارة تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# جدول المستخدمين في قاعدة البيانات
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
# استخدام مفتاح الـ API الحقيقي المباشر والفعال لمعالجة الطلبات
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

        # تضمين رابط تواصل زبونك بشكل خفيف وسريع جداً
        link_text = f"\nرابط التواصل: {user_link}" if user_link and user_link.strip() else ""

        # برومبت مخفف وسريع جداً ليعود الموقع طلقة وخفيفاً كما كان في البداية وبأحدث موديل معتمد
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
    
