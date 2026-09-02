import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from google import genai
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# --- إعدادات الحماية وقاعدة البيانات ---
app.config['SECRET_KEY'] = 'AkramFlowSuperSecretKey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# --- إعداد نظام إدارة تسجيل الدخول ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- جدول المستخدمين في قاعدة البيانات ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- أمر سحري لإنشاء قاعدة البيانات تلقائياً عند التشغيل ---
with app.app_context():
    db.create_all()

# --- إعدادات مخرجات الـ API لـ Gemini ---
API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

# ================= مسارات الموقع (ROUTES) =================

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            return "هذا المستخدم موجود بالفعل!"
            
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "اسم المستخدم أو كلمة المرور غير صحيحة!"
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
@login_required
def generate_content():
    try:
        data = request.get_json(silent=True) or {}
        user_idea = data.get('idea', '')
        content_type = data.get('contentType', 'محتوى تسويقي')
        tone = data.get('tone', 'إقناعي واحترافي للبيع')
        
        # صياغة الطلب الذكي لـ Gemini بناءً على مدخلات المستخدم بالكامل
        prompt = f"قم بإنشاء وتأليف ({content_type}) عن فكرة المشروع التالية: ({user_idea}). استخدم في الكتابة أسلوب ونبرة: ({tone})."
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
           
