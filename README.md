# VORTEX
### CS50x 2026 — Final Project

## Video Demo:
- https://youtu.be/sUh0Bc4E2A0

---

# Description

VORTEX is a modern Flask-based e-commerce platform developed as my CS50x final project.

The project was designed to simulate a real-world production-ready online store rather than a simple academic prototype. The platform allows users to browse products, select variants such as sizes, upload custom clothing designs, and place orders through a responsive shopping experience.

The backend is built using Flask with a modular project structure to improve maintainability and scalability. The application uses Turso (LibSQL) for database management, Cloudinary for image hosting, and Telegram Bot API integration for automated order notifications.

A major focus during development was security and deployment readiness. The project includes CSRF protection, rate-limited admin authentication using Flask-Limiter, environment-based secret management, secure production cookie settings, and input validation for cart operations.

The admin dashboard allows product management while Telegram notifications automatically deliver formatted order details to store owner chat IDs whenever a customer places an order.

The frontend was designed to be responsive across desktop and mobile devices, with an emphasis on clean layouts and simplified user interactions.

During development, I made several design decisions regarding scalability, deployment structure, media storage, and backend organization. For example, I chose Cloudinary instead of local file storage to simplify deployment and improve media management. I also separated configuration, extension initialization, utility logic, and route handling into dedicated files to keep the codebase organized and easier to maintain.

This project combines concepts learned throughout CS50x including Python, Flask, SQL, APIs, web development, security practices, and deployment workflows.

---

# Features

* Product catalog and product variants
* Shopping cart system
* Custom design uploads
* Admin dashboard
* Cloudinary image uploads
* Turso database integration
* Telegram order notifications
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
* Requests

## Database

* Turso (LibSQL)

## Media Storage

* Cloudinary

## Notifications

* Telegram Bot API

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
├── helpers.py
├── cloudinary_utils.py
├── requirements.txt
├── vercel.json
├── routes/
├── templates/
├── static/
├── database/
└── .env.example
```

---

# File Overview

## app.py
- Main Flask application entry point. Responsible for initializing the application, registering routes, loading configuration, and starting the server.

## wsgi.py
- WSGI entry point used for production deployment on Vercel.

## config.py
- Contains environment-based configuration logic, secret loading, production settings, and application configuration values.

## extensions.py
- Initializes reusable Flask extensions such as CSRF protection and rate limiting.

## helpers.py
- Contains reusable helper functions used across different parts of the application.

## cloudinary_utils.py
- Handles Cloudinary upload functionality and media management operations.

## requirements.txt
- Lists all Python dependencies required to run the application.

## vercel.json
- Defines the deployment configuration used by Vercel for routing and Python server execution.

## routes/
- Contains the application's route modules. Separating routes into dedicated files improves maintainability and keeps the application structure modular.

## templates/
- Contains Jinja2 HTML templates used to render frontend pages and admin dashboard views.

## static/
- Stores frontend assets including CSS, JavaScript, uploaded assets, and images used by the interface.

## database/
- Contains SQL schema files and database-related setup logic.

---

# Environment
Variables

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

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID_1=your_chat_id
TELEGRAM_CHAT_ID_2=your_second_chat_id
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

# Telegram Order Notifications

VORTEX includes a Telegram notification system that automatically sends a formatted order summary to store owner chat IDs whenever a new order is placed.

Notifications include:

* Order ID
* Customer information
* Ordered products
* Quantities and sizes
* Total price
* Delivery address
* Cairo timezone timestamp

The notification system uses:

* Telegram Bot API
* HTML-formatted messages
* Multi-chat support
* Safe error handling
* Requests-based API calls

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

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID_1=
TELEGRAM_CHAT_ID_2=
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
* Keep Telegram bot credentials private
* Always deploy with `FLASK_ENV=production`

---

# Future Improvements

* User authentication system
* Order tracking
* Payment integration
* Email notifications
* Admin analytics

---

# License

This project is licensed under the MIT License.
If you fork or reuse this project, you must remove all VORTEX branding,
personal links, and author-specific content before publishing.

---

# Author

Bassam Tarek Al-Arabi
