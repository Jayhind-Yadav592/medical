# AuraHealth™ — Precision Pharmacy & Digital Healthcare Platform

> **AuraHealth** is an enterprise-grade, modern digital online pharmacy and clinical telehealth web application built with **Python 3.11**, **Django 5.0**, **Django REST Framework**, and **PostgreSQL**.
> 
> Designed from scratch with an original high-trust clinical visual language, responsive design system, real-time AJAX search autocomplete, live slide-over cart drawer, instant prescription upload & triage workflow, telehealth doctor booking, and end-to-end order tracking.

---

## 🔬 Key Architectural Highlights

1. **Original Visual Design System (Phase 1 & Phase 2)**:
   - Deep Clinical Navy (`#0B2545`, `#134074`), Luminous Cyan (`#0EA5E9`), Certified Emerald (`#10B981`), Amber (`#F59E0B`), and Warm Coral (`#F43F5E`).
   - Clean typographic scale using Google's *Plus Jakarta Sans*.
   - Micro-interactive glassmorphism cards, prescription dropzone widgets, pulsing live indicators, and subtle transitions.

2. **14+ Master Homepage Sections**:
   - **Top Utility Bar & Global Header**: Emergency 24/7 hotline, delivery location selector, search bar with live auto-suggest.
   - **3-Column Asymmetrical Hero**: Headline, certified trust pills, interactive 1-Click Prescription Upload dropzone, and on-duty live pharmacist status badge.
   - **Interactive Symptom Diagnostic Quick Finder**: One-click condition chips (Headache, Cough & Cold, Diabetes, Allergies, Joint Pain).
   - **Healthcare Services Grid**: e-Prescription fulfillment, 15-min cold-chain delivery, telehealth consults, chronic care refills, diagnostics.
   - **Curated Medicine & Wellness Showcase**: Multi-tab filtering, stock indicators, Rx badges, quantity selectors, and instant Add to Cart.
   - **Why Choose AuraHealth**: Double-check pharmacist validation, Temperature-Shield™ cold chain, HIPAA encryption.
   - **Telehealth Specialist Booking Grid**: Doctor profiles, experience, next available slots, and 1-click appointment booking modal.
   - **Digital Healthcare App & Smart Refill Banner**: Mobile experience, smart pill alarms, and WhatsApp 1-tap refills.
   - **Clinical Statistics & Real-time Impact Counters**: 99.8% genuine guarantee, 45k+ prescriptions dispensed, 4.96/5 patient rating.
   - **Verified Patient & Practitioner Testimonials**: Real patient stories with condition tags.
   - **Doctor-Reviewed Health Articles & Journal**: Evidence-based medical guides and fact-checked wellness articles.
   - **Emergency Pharmacist Hotline CTA Banner**: Instant triage trigger and telephone call action.
   - **Deep Obsidian Footer & Newsletter Subscription**: Regulatory disclosures, licensing, SSL badges, and payment gateways.

3. **Robust Backend Architecture (Django + DRF + PostgreSQL)**:
   - Modular Apps: `apps.core`, `apps.pharmacy`, `apps.orders`, `apps.telehealth`, `apps.articles`, `apps.api`.
   - Custom User model with blood group, allergies, patient/doctor roles, and multiple addresses.
   - Full REST API with DRF routers, serializers, and JWT/Session authentication.
   - Auto-adaptive database engine: Native PostgreSQL with graceful SQLite fallback.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Django 5.0.6, Django REST Framework 3.14.0
- **Database**: PostgreSQL (with automatic connection fallback for seamless local development)
- **Frontend**: HTML5, CSS3, Modern ES6+ JavaScript, Bootstrap 5.3, FontAwesome 6 Pro, Plus Jakarta Sans
- **Static Assets & Media**: WhiteNoise, Pillow

---

## 🚀 Quick Start Guide

### 1. Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 2. Seed Medical Catalogue & Test Accounts
```powershell
python manage.py seed_medical_data
```
*This populates the database with 12+ categorized medicines, real brands, certified doctors, clinical journal articles, and test accounts.*

**Demo Credentials**:
- **Administrator / Pharmacist**: `admin` / `admin`
- **Patient User**: `patient_sarah` / `password123`

### 3. Run Development Server
```powershell
python manage.py runserver
```
Navigate to: **`http://127.0.0.1:8000/`**

---

## 📡 REST API Endpoints Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/products/` | `GET` | List & filter medicines by category, Rx required, price, search |
| `/api/search/autocomplete/?q=<term>` | `GET` | Instant autocomplete search results with images and pricing |
| `/api/cart/` | `GET`, `POST`, `PATCH`, `DELETE` | Slide-over cart state, add items, update quantities, clear |
| `/api/wishlist/` | `GET`, `POST` | Toggle and retrieve saved items |
| `/api/prescriptions/upload/` | `POST` | Multipart file upload with patient metadata & Rx reference ID |
| `/api/consultations/book/` | `POST` | Schedule virtual telehealth consultation with doctor |
| `/api/orders/checkout/` | `POST` | Create complete order, order items, and tracking number from active cart |
| `/api/orders/track/<order_number>/` | `GET` | Live 5-stage progress timeline and item verification details |
| `/api/newsletter/subscribe/` | `POST` | Subscribe email to clinical newsletter digest |
| `/api/auth/login/` & `register/` | `POST` | Patient authentication and registration |

---

## 🧪 Automated Integration Tests

Run the complete test suite:
```powershell
python manage.py test apps
```
*All 7 core test suites cover homepage rendering, category filters, autocomplete APIs, cart calculations, prescription multipart uploads, consultation bookings, and order tracking timelines.*
