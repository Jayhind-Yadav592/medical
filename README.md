# Antixor MedOS™ — Precision Pharmacy & Digital Healthcare Platform

[![CI/CD Pipeline](https://github.com/Jayhind-Yadav592/medical/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Jayhind-Yadav592/medical/actions/workflows/ci-cd.yml)
[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django Framework](https://img.shields.io/badge/Django-5.0.6-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![REST API Ready](https://img.shields.io/badge/REST_API-DRF_3.14-FF5722?logo=django&logoColor=white)](https://github.com/Jayhind-Yadav592/medical)
[![Docker Containerized](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Tests Passing](https://img.shields.io/badge/Unit_Tests-31%2F31_Passing-10B981?logo=pytest&logoColor=white)](https://github.com/Jayhind-Yadav592/medical)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Antixor MedOS** is an enterprise-grade, integrated digital healthcare operating platform and precision dispensary network built with **Python 3.11**, **Django 5.0**, **Django REST Framework**, **ReportLab 5**, **Pillow**, **PostgreSQL**, and **Docker**.
>
> Built for clinical safety, cold-chain medication compliance, and seamless patient triage, featuring **Enterprise REST API Architecture**, **ReportLab PDF Invoicing & Digitally-Signed e-Prescriptions**, **AI Vision Prescription OCR**, **Stripe & Razorpay Multi-Payment Gateways with Webhooks**, and **24/7 Telehealth Consultations**.

---

## 🔬 Key Architectural Highlights & Resume Features

### 1. ⚡ Comprehensive Clinical REST API Architecture (`/api/`)
- Built with **Django REST Framework** across 9 clinical API domains:
  - `Pharmacy & Catalog`, `Cart & Wishlist`, `Prescriptions & Safety`, `Telehealth & Consultations`, `Orders & Tracking`, `Facilities & Emergency SOS`, `Patient EHR & Intake`, `Authentication & User`, `Articles & Communications`.

### 2. 📄 Clinical ReportLab PDF Generator Engine (`apps/orders/pdf_generator.py`)
- **Official Pharmacy Tax Invoices (`/order/invoice/<no>/pdf/`)**:
  - Antixor clinical letterhead, dispensary license (`#NY-PHARM-9842`), DEA registry, itemized medication table (dosage form, unit price, subtotal), cold-chain compliance notice ($2^\circ\text{C}-8^\circ\text{C}$), digital tamper-evident QR verification code, and electronic pharmacist seal.
- **Digitally-Signed Medical e-Prescription (Rx) (`/prescription/<id>/pdf/`)**:
  - Physician credentials, ℞ header, SIG dosage instructions, refill permissions, SHA-256 cryptographic verification stamp, and Title 21 CFR Part 1311 compliance footer.

### 3. 🧠 Clinical AI Vision & Prescription OCR Parser (`/api/prescriptions/ai-ocr/`)
- **Image Preprocessing & OCR**: Analyzes uploaded doctor prescription slips and removes artifacts using Pillow (`PIL`).
- **Clinical NLP Entity Extraction**: Detects physician DEA credentials, clinic address, patient demographics, and medication signature instructions (SIG).
- **Catalog Inventory Matcher**: Automatically maps extracted active molecules (*Amoxicillin*, *Paracetamol*, *Vitamin D3*, *Salbutamol*) to live database `Product` SKUs, live prices, and real-time stock levels.
- **1-Click Auto-Cart**: Instant **"Add All Available to Cart"** button converts parsed Rx medications directly into cart items.

### 4. 💳 Multi-Payment Gateway Architecture (`apps/orders/payment_gateways.py`)
- **Stripe Gateway**: PaymentIntent session creation, 3D Secure test card autofill simulator (`4242 4242...`), and webhook reconciliation (`/api/webhooks/stripe/`).
- **Razorpay Gateway**: UPI VPA and NetBanking order payload (`order_AUR_...`), paise subunit calculation, and HMAC-SHA256 signature verification (`/api/webhooks/razorpay/`).
- **Apple Pay & Google Pay**: 1-touch biometric token simulation.
- **Cash on Delivery (COD)**: Temperature-sealed verification dispatch.
- **Automated Ledger**: Instant registration in `OrderStatusHistory`.

### 5. 🐳 Production Docker & CI/CD Orchestration
- **Multi-Stage Dockerfile**: Python 3.11-slim base with unprivileged user (`appuser`), healthcheck probe, and Gunicorn WSGI.
- **Docker Compose**: Orchestrates Django Web, PostgreSQL 16 Alpine, Redis 7 Alpine, and Nginx SSL Reverse Proxy.
- **GitHub Actions (`.github/workflows/ci-cd.yml`)**: Automated pipeline running 31 unit tests, Django system checks, OpenAPI schema validation, and Docker container build verification on every push.

---

## 🛠️ Tech Stack & Dependencies

- **Backend**: Python 3.11, Django 5.0.6, Django REST Framework 3.14.0
- **API Documentation**: `drf-spectacular` (OpenAPI 3.0, Swagger UI, Redoc)
- **PDF Generation**: ReportLab 5.0.1 (Platypus Flowable Architecture)
- **Image Processing & Vision OCR**: Pillow 12.3.0
- **Database**: PostgreSQL 16 (Native) with SQLite3 auto-fallback for local development
- **Cache & Message Broker**: Redis 7.0
- **Web Server & Reverse Proxy**: Gunicorn WSGI 25.0.2 + Nginx 1.25 (Gzip, SSL, Static Caching)
- **CI/CD**: GitHub Actions Workflows

---

## 🚀 Quick Start Guide

### Option A: Standard Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Jayhind-Yadav592/medical.git
   cd medical
   ```

2. **Create Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv env
   # Windows:
   .\env\Scripts\activate
   # Linux/macOS:
   source env/bin/activate

   pip install -r requirements.txt
   ```

3. **Database Migrations & Test Seeding**:
   ```bash
   python manage.py migrate
   python manage.py seed_medical_data
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```
   - **Web Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
   - **Redoc UI**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

---

### Option B: Docker Compose (Production Environment)

```bash
# Build and run all microservices (Django, PostgreSQL, Redis, Nginx)
docker compose up --build -d
```

---

## 📡 Key REST API Endpoints Overview

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Catalog** | `/api/products/` | `GET` | Filter medicines by Category, Rx requirement, Price, Stock |
| **Search** | `/api/search/autocomplete/?q=<term>` | `GET` | Real-time search suggestions with thumbnail and active salt |
| **Cart** | `/api/cart/` | `GET`, `POST`, `DELETE` | Shopping cart operations & cold-chain fee calculations |
| **AI OCR** | `/api/prescriptions/ai-ocr/` | `POST` | AI Vision Prescription Scanner with auto-cart population |
| **PDF** | `/api/orders/<order_no>/invoice/pdf/` | `GET` | Download official clinical tax invoice PDF |
| **PDF** | `/api/prescriptions/<id>/pdf/` | `GET` | Download digitally-signed doctor e-prescription PDF |
| **Payment** | `/api/orders/payment/create-intent/` | `POST` | Initialize Stripe / Razorpay / Apple Pay payment session |
| **Payment** | `/api/orders/payment/verify/` | `POST` | Verify payment signature and reconcile order status |
| **Webhooks**| `/api/webhooks/stripe/` | `POST` | Stripe Webhook reconciliation listener |
| **Webhooks**| `/api/webhooks/razorpay/` | `POST` | Razorpay Webhook reconciliation listener |
| **Facilities** | `/api/facilities/nearest/?lat=...&lng=...` | `GET` | Geolocation radar for nearest pharmacy and emergency center |
| **SOS** | `/api/emergency/sos/` | `POST` | 1-Touch Emergency Ambulance & Hospital Triage Dispatch |

---

## 🧪 Automated Unit Test Suite

Run the full automated test suite covering all apps and endpoints:
```bash
python manage.py test --verbosity=2
```

```
Found 31 test(s).
System check identified no issues (0 silenced).
...............................
----------------------------------------------------------------------
Ran 31 tests in 16.8s

OK (31/31 Passing - 100% Success)
```

---

## 📄 License & Disclaimer

- Licensed under the **MIT License**.
- Developed as a digital healthcare precision platform showcase. All sample pharmaceutical data is for clinical demonstration and testing purposes.
