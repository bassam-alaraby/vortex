# VORTEX

### A Flask-based e-commerce platform

## Video Demo

[Watch the demo on YouTube](https://youtu.be/sUh0Bc4E2A0)

---

# Description

VORTEX is a Flask-based e-commerce platform originally developed as a CS50x final project.

The project was built around a practical e-commerce use case rather than a simple academic prototype. It provides a storefront where users can browse products, select variants such as sizes, upload custom clothing designs, and place orders through a responsive shopping experience.

The backend is built with Flask using a modular project structure designed to improve maintainability and scalability. The application uses Turso (LibSQL) for database management, Cloudinary for image hosting, and the Telegram Bot API for automated order notifications.

Security and deployment readiness were important considerations throughout development. The project includes CSRF protection, rate-limited admin authentication using Flask-Limiter, environment-based secret management, secure production cookie settings, and input validation for cart operations.

The admin dashboard provides product and order management capabilities, while Telegram notifications can automatically deliver formatted order details to one or more configured store-owner chat IDs whenever a customer places an order.

The frontend was designed to be responsive across desktop and mobile devices, with an emphasis on clean layouts and straightforward user interactions.

The project also demonstrates practical decisions around deployment, media storage, application structure, and backend organization. For example, Cloudinary was used instead of local file storage to simplify deployment and centralize media management. Configuration, extension initialization, utility logic, and route handling are separated into dedicated modules to keep the codebase organized.

VORTEX combines concepts covered throughout CS50x, including Python, Flask, SQL, APIs, web development, security practices, version control, and deployment workflows.

---

# Features

## Storefront

* Product catalog
* Product variants and sizes
* Shopping cart system
* Custom clothing design uploads
* Responsive frontend

## Administration

* Admin dashboard
* Product management
* Order management
* Protected admin authentication

## Integrations

* Turso (LibSQL) database
* Cloudinary image hosting
* Telegram order notifications

## Security

* CSRF protection
* Rate-limited admin authentication
* Input validation
* Environment-based secret management
* Secure production cookie configuration

---

# Tech Stack

## Backend

* Python
* Flask
* Flask-WTF
* Flask-Limiter
* Requests

## Frontend

* HTML
* CSS
* JavaScript
* Jinja2

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

| File / Directory      | Purpose                                                  |
| --------------------- | -------------------------------------------------------- |
| `app.py`              | Main Flask application entry point                       |
| `wsgi.py`             | WSGI entry point for deployment                          |
| `config.py`           | Environment-based configuration and application settings |
| `extensions.py`       | Flask extension initialization                           |
| `helpers.py`          | Shared application utilities                             |
| `cloudinary_utils.py` | Cloudinary upload and media management functions         |
| `requirements.txt`    | Python dependencies                                      |
| `vercel.json`         | Vercel deployment configuration                          |
| `routes/`             | Application route modules                                |
| `templates/`          | Jinja2 HTML templates                                    |
| `static/`             | Frontend assets such as CSS and JavaScript               |
| `database/`           | Database schema and setup files                          |

---

# Configuration

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

### Telegram Chat Configuration

The application supports sending order notifications to multiple Telegram chats.

* `TELEGRAM_CHAT_ID_1` is required when Telegram notifications are enabled.
* `TELEGRAM_CHAT_ID_2` is optional.
* If only one chat is needed, leave `TELEGRAM_CHAT_ID_2` unset.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/bassam-alaraby/vortex.git
cd vortex
```

## 2. Create a virtual environment

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

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file using the configuration described above.

## 5. Run the application

```bash
python app.py
```

Or:

```bash
flask run
```

---

# Database Setup

VORTEX uses Turso (LibSQL) for database storage.

After creating a Turso database:

1. Create the required database.
2. Configure `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`.
3. Execute the contents of `database/schema.sql` against the database.

The schema only needs to be initialized once for a new database.

---

# Cloudinary Media Storage

VORTEX uses Cloudinary for image storage instead of relying on local file storage.

Images are organized into dedicated folders:

```text
products/
custom_designs/
```

Examples:

* Product images → `products/`
* User custom designs → `custom_designs/`

This keeps uploaded media separate from the application filesystem and simplifies deployment.

---

# Telegram Order Notifications

VORTEX includes a Telegram notification system that can automatically send a formatted order summary to configured store-owner chat IDs whenever a new order is placed.

Notifications can include:

* Order ID
* Customer information
* Ordered products
* Quantities and sizes
* Total price
* Delivery address
* Order timestamp

The notification system uses:

* Telegram Bot API
* HTML-formatted messages
* Multi-chat support
* Safe error handling
* Requests-based API calls

A single Telegram chat is sufficient, while a second chat can be configured when notifications need to be delivered to multiple recipients.

---

# Security

The project includes several security measures:

* CSRF protection using Flask-WTF
* Secure session cookies in production
* Environment-based secret management
* Rate-limited admin authentication using Flask-Limiter
* Input validation for cart operations

Admin authentication is protected by request rate limiting to reduce the risk of repeated login attempts.

---

# Deployment

The project includes a Vercel deployment configuration through `vercel.json`.

For deployment, configure the required environment variables in the hosting platform rather than committing sensitive credentials to the repository.

---

# License

This project is licensed under the MIT License.

If you fork or reuse this project, you must remove all VORTEX branding, personal links, and author-specific content before publishing.

---

# Author

Bassam Tarek Al-Araby
