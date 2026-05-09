# VORTEX

Modern Flask-based e-commerce platform with secure admin management, Cloudinary media storage, Turso database integration, and production-ready deployment support.

---

## Features

* Product catalog and product variants
* Shopping cart system
* Custom design uploads
* Admin dashboard
* Cloudinary image uploads
* Turso database integration
* CSRF protection
* Rate-limited admin login
* Production-ready configuration
* Responsive frontend

---

# Tech Stack

## Backend

* Python
* Flask
* Flask-WTF
* Flask-Limiter

## Database

* Turso (LibSQL)

## Media Storage

* Cloudinary

## Deployment

* Vercel

---

# Project Structure

```text
VORTEX/
├── app.py
├── wsgi.py
├── config.py
├── extensions.py
├── requirements.txt
├── routes/
├── templates/
├── static/
├── database/
├── cloudinary_utils.py
└── .env.example
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your_secret_key

ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_ME_STRONG_PASSWORD

FLASK_ENV=development

TURSO_DATABASE_URL=your_database_url
TURSO_AUTH_TOKEN=your_auth_token

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/bassam-alaraby/vortex.git
cd VORTEX
```

## 2. Create virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the application

```bash
python app.py
```

Or:

```bash
flask run
```

---

# Database Setup (Turso)

After creating your Turso database, run the schema manually:

1. Open your database on [Turso Dashboard](https://app.turso.tech)
2. Go to **Edit Data** tab
3. Copy the contents of `database/schema.sql`
4. Paste and click **Run**

This only needs to be done once.

---

# Cloudinary Upload Structure

Images are organized into folders:

```text
products/
custom_designs/
```

Examples:

* Product images → `products/`
* User custom designs → `custom_designs/`

---

# Security

The project includes:

* CSRF protection
* Secure session cookies in production
* Environment-based secrets
* Admin login rate limiting
* Input validation for cart operations

Admin login is protected with:

```text
5 requests per minute
```

using Flask-Limiter.

---

# Deployment (Vercel)

## Required Environment Variables

Set these inside your Vercel project settings:

```env
SECRET_KEY=
ADMIN_USERNAME=
ADMIN_PASSWORD=
FLASK_ENV=production
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
```

---

# Production Notes

* Do not commit `.env`
* Use strong admin credentials
* Keep Cloudinary credentials private
* Always deploy with `FLASK_ENV=production`

---

# Future Improvements

* User authentication system
* Order tracking
* Payment integration
* Redis-based rate limiting
* Email notifications
* Admin analytics

---

# License

This project is intended for educational, portfolio, and personal business purposes.

---

# Author

Bassam Tarek Al-Arabi
