# 🛒 ANJAC Home Appliances

A Django-based e-commerce application for browsing, searching, and purchasing home appliances.  
Includes features like product listings, cart management, checkout, orders tracking, and user authentication.

---

## 📂 Project Structure

```
ANJAC-HOME-APPLIANCES/
│
├── anjac_home_appliances/    # Main Django project settings & config
│   ├── settings.py           # Django settings (update DB, static/media paths here)
│   ├── urls.py               # Project-level URL routing
│   ├── wsgi.py                # WSGI entry point
│
├── shop/                     # Main app for e-commerce logic
│   ├── templates/            # HTML templates (Bootstrap + Django template tags)
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── orders.html
│   │   └── product_detail.html
│   ├── views.py               # View functions for handling requests
│   ├── models.py              # Database models (Product, Order, Cart, etc.)
│   ├── forms.py               # Django forms for authentication & checkout
│   ├── urls.py                # App-level URL routes
│   ├── admin.py               # Django admin configuration
│
├── media/                     # Uploaded media files (product images, logo, etc.)
│   └── products/anjac-logo.png
│
├── static/                    # Static assets (CSS, JS, icons, etc.)
│
├── db.sqlite3                  # SQLite database (default)
├── manage.py                   # Django management CLI
└── README.md                   # Project documentation
```

---

## 🚀 Features

- **Product Catalog**
  - List all products
  - View product details
  - Search products by name, brand, or category
- **User Authentication**
  - Register/Login/Logout
  - Profile management
- **Shopping Cart**
  - Add to cart
  - Edit quantity
  - Save for later
  - Remove items
- **Checkout & Orders**
  - Address selection
  - Order summary
  - Order history & status tracking
- **Responsive UI**
  - Bootstrap 5 for mobile-friendly design
  - Flipkart/Amazon-inspired navbar and layout
- **Media Handling**
  - Product images & logo stored in `/media/products/`

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/rajaCDS/anjac-home-appliances.git
cd anjac-home-appliances
```

### 2️⃣ Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:

pip install -r requirements.txt
```

> **Note:** If `requirements.txt` is missing, generate it:
```bash
pip freeze > requirements.txt
```

### 3️⃣ Configure Settings
Edit `anjac_home_appliances/settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 4️⃣ Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Create Superuser (for Admin Access)
```bash
python manage.py createsuperuser
```

### 6️⃣ Run Development Server
```bash
python manage.py runserver
```
Now visit:  
```
http://127.0.0.1:8000
```

---

## 🖼️ Adding the Logo
Place your logo in:
```
/media/products/anjac-logo.png
```
In `base.html`:
```html
<img src="/media/products/anjac-logo.png" alt="ANJAC Logo" width="60" height="60">
```

---

## 📌 Tech Stack
- **Backend:** Django 5.x (Python 3.x)
- **Database:** SQLite (default, can switch to MySQL/PostgreSQL)
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome
- **Media:** Django's built-in media handling

---

🎨 Jazzmin Admin Theme Setup

We use django-jazzmin
 to give the admin panel a modern look.

1️⃣ Install Jazzmin
pip install django-jazzmin


3️⃣ Run Collectstatic
python manage.py collectstatic --noinput


5️⃣ Run the Server
python manage.py runserver


Now open:

http://127.0.0.1:8000/admin/


🎉 You’ll see a modern Jazzmin-powered Admin Panel.

---

## 📄 License
This project is licensed under the MIT License.

---
