# Vortex

مشروع متجر بسيط مبني بـ Flask.

## التشغيل السريع (Codespaces أو Local)

1. افتح التيرمنال داخل مجلد المشروع:

```bash
cd vortex
```

2. أنشئ virtual environment:

```bash
python3 -m venv venv
```

3. فعّل البيئة:

```bash
source venv/bin/activate
```

4. نزّل المكتبات من ملف المتطلبات:

```bash
pip install -r requirements.txt
```

5. جهّز قاعدة البيانات (أول مرة فقط):

```bash
python3 database/init_db.py
```

6. شغّل التطبيق:

```bash
python3 app.py
```

7. افتح المتصفح على:

```text
http://127.0.0.1:5000
```

## المكتبات المطلوبة

المشروع يحتاج فقط:

- `Flask`
- `cs50`
