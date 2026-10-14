from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "elbadry_secret_admin_key_2026_secure"

# قاعدة بيانات الإعلانات المؤقتة (تتحول لاحقاً لقاعدة بيانات دائمة عند الربط الكامل)
ads_db = []

# بيانات لوحة التحكم السرية الخاصة بك وحدك
ADMIN_USER = "elbadry"
ADMIN_PASS = "123456" 

# رقم فودافون كاش الحقيقي الخاص بك لاستلام أرباح تجديد الإعلانات
VODAFONE_CASH_NUMBER = "01022829709"

home_html = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>منصة الإعلانات التجارية الذكية - البدري</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f4f4f9; text-align: center; padding: 20px; }
        .container { background: white; padding: 25px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); width: 420px; text-align: left; }
        input, textarea { width: 100%%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #28a745; color: white; border: none; padding: 12px; width: 100%%; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; }
        .ad-card { background: #e9ecef; padding: 12px; margin: 10px 0; border-radius: 5px; font-size: 14px; text-align: right; }
        .expired { color: red; font-weight: bold; }
        .active { color: green; font-weight: bold; }
        .pay-box { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px; margin-top: 8px; border-radius: 5px; font-size: 13px; color: #856404; }
        .admin-link { margin-top: 20px; display: block; font-size: 13px; color: #6c757d; text-decoration: none; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align: center; color: #333;">📢 سوق الإعلانات الذكي</h2>
        
        <h3>أضف إعلانك المجاني (تجربة لمدة 30 يوم)</h3>
        <form method="post" action="/add_ad">
            <input type="text" name="title" placeholder="اسم المحل أو النشاط التجاري" required>
            <textarea name="description" placeholder="تفاصيل الخدمة أو المنتجات..." required></textarea>
            <input type="text" name="phone" placeholder="رقم التليفون أو الواتساب" required>
            <!-- خانة حماية خفية ضد الروبوتات والسبام -->
            <input type="text" name="bot_check" style="display:none;" value="">
            <button type="submit">نشر الإعلان مجاناً</button>
        </form>

        <hr>
        <h3>📋 دليل الإعلانات والنشاطات</h3>
        {% for ad in ads %}
            <div class="ad-card">
                <b>📌 النشاط: {{ ad.title }}</b><br>
                💬 الوصف: {{ ad.description }}<br>
                📞 للتواصل: {{ ad.phone }}<br>
                <small>📅 تاريخ النشر: {{ ad.date_added }} | ⌛ ينتهي في: {{ ad.date_expiry }}</small><br>
                
                {% if ad.is_active %}
                    <span class="active">● الحالة: نشط ومتاح للعامة</span>
                {% else %}
                    <span class="expired">● الحالة: انتهت المدة المجانية (موقوف مؤقتاً)</span>
                    <div class="pay-box">
                        <b>⚠️ لتجديد إعلانك لمدة شهر إضافي:</b><br>
                        - تحويل مبلغ الاشتراك عبر <b>فودافون كاش</b> على رقم الإدارة: <b>{{ vf_number }}</b><br>
                        - بعد التحويل، تواصل مع صاحب المنصة لتفعيل إعلانك فوراً.
                    </div>
                {% endif %}
            </div>
        {% else %}
            <p style="text-align:center; color: #777;">لا توجد إعلانات مسجلة حالياً.</p>
        {% endfor %}

        <a class="admin-link" href="/admin_login">🔐 دخول لوحة تحكم صاحب الموقع (الأدمن)</a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    now = datetime.now()
    for ad in ads_db:
        expiry_date = datetime.strptime(ad['date_expiry'], "%Y-%m-%d")
        if now > expiry_date:
            ad['is_active'] = False
        else:
            ad['is_active'] = True
    return render_template_string(home_html, ads=ads_db, vf_number=VODAFONE_CASH_NUMBER)

@app.route("/add_ad", methods=["POST"])
def add_ad():
    # نظام حماية ضد الروبوتات الآلية (Bot Trap)
    if request.form.get("bot_check"):
        return "Spam or Bot detected and blocked."
        
    title = request.form.get("title")
    description = request.form.get("description")
    phone = request.form.get("phone")
    
    now = datetime.now()
    expiry = now + timedelta(days=30)  # صلاحية مجانية 30 يوم
    
    new_ad = {
        "id": len(ads_db) + 1,
        "title": title,
        "description": description,
        "phone": phone,
        "date_added": now.strftime("%Y-%m-%d"),
        "date_expiry": expiry.strftime("%Y-%m-%d"),
        "is_active": True
    }
    
    ads_db.append(new_ad)
    return redirect(url_for('index'))

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "<script>alert('بيانات الدخول خاطئة!'); window.location='/admin_login';</script>"
            
    return """
    <html lang="ar" dir="rtl"><body style="font-family:Tahoma; text-align:center; padding:50px; background:#f4f4f9;">
        <div style="background:white; padding:30px; display:inline-block; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
            <h3>🔐 تسجيل دخول صاحب الموقع (الأدمن)</h3>
            <form method="post">
                <input type="text" name="username" placeholder="اسم المستخدم" required style="padding:10px; margin:5px; width:250px;"><br>
                <input type="password" name="password" placeholder="كلمة المرور السرية" required style="padding:10px; margin:5px; width:250px;"><br><br>
                <button type="submit" style="background:#007bff; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">دخول لوحة التحكم</button>
            </form>
            <br><a href="/">← العودة للموقع الرئيسي</a>
        </div>
    </body></html>
    """

@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
        
    ads_list_html = ""
    for ad in ads_db:
        ads_list_html += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding:10px;">{ad['title']}</td>
            <td style="padding:10px;">{ad['phone']}</td>
            <td style="padding:10px;">{ad['date_expiry']}</td>
            <td style="padding:10px;">{'نشط' if ad['is_active'] else 'منتهي'}</td>
            <td style="padding:10px;">
                <a href="/admin/renew/{ad['id']}" style="background:green; color:white; padding:5px 10px; text-decoration:none; border-radius:3px;">تجديد شهر</a>
                <a href="/admin/delete/{ad['id']}" style="background:red; color:white; padding:5px 10px; text-decoration:none; border-radius:3px; margin-right:5px;">حذف</a>
            </td>
        </tr>
        """
        
    return f"""
    <html lang="ar" dir="rtl"><body style="font-family:Tahoma; padding:30px; background:#f4f4f9;">
        <div style="max-width:800px; margin:auto; background:white; padding:25px; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
            <h2>⚙️ لوحة التحكم الملكية الخاصة بك (الأدمن)</h2>
            <p>أهلاً بك يا أستاذ البدري. رقم فودافون كاش الخاص بك لاستلام أرباح التجديد هو: <b>{VODAFONE_CASH_NUMBER}</b></p>
            <a href="/admin_logout" style="background:#dc3545; color:white; padding:8px 15px; text-decoration:none; border-radius:5px; display:inline-block; margin-bottom:15px;">تسجيل خروج</a>
            <table width="100%" style="border-collapse: collapse; text-align:right;">
                <tr style="background:#007bff; color:white;">
                    <th style="padding:10px;">اسم النشاط</th>
                    <th style="padding:10px;">رقم التليفون</th>
                    <th style="padding:10px;">تاريخ الانتهاء</th>
                    <th style="padding:10px;">الحالة</th>
                    <th style="padding:10px;">التحكم</th>
                </tr>
                {ads_list_html if ads_list_html else '<tr><td colspan="5" style="text-align:center; padding:20px;">لا توجد إعلانات مسجلة بعد</td></tr>'}
            </table>
            <br><a href="/" style="color:#007bff; text-decoration:none;">← الانتقال للموقع العام</a>
        </div>
    </body></html>
    """

@app.route("/admin/renew/<int:ad_id>")
def admin_renew(ad_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    for ad in ads_db:
        if ad['id'] == ad_id:
            current_expiry = datetime.strptime(ad['date_expiry'], "%Y-%m-%d")
            new_expiry = max(datetime.now(), current_expiry) + timedelta(days=30)
            ad['date_expiry'] = new_expiry.strftime("%Y-%m-%d")
            ad['is_active'] = True
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete/<int:ad_id>")
def admin_delete(ad_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    global ads_db
    ads_db = [ad for ad in ads_db if ad['id'] != ad_id]
    return redirect(url_for('admin_dashboard'))

@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
