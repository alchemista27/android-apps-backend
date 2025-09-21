# PJBLMS Backend

Backend API untuk sistem manajemen proyek dan materi pembelajaran berbasis role (Admin, Dosen, Mahasiswa). Dibangun menggunakan **FastAPI** dengan database **SQLAlchemy**.

---

## 🚀 Fitur Utama

### 1. Autentikasi & User
- Register / Login (JWT Bearer Token)
- Role-based access control: Admin, Dosen, Mahasiswa
- Endpoint untuk mendapatkan info user saat ini (`/auth/me`)

### 2. Project Management
- CRUD Project (`/projects`) → Admin/Dosen only
- Assign Project ke Mahasiswa (`/projects/assign`)
- Role-based access untuk GET list project (Mahasiswa hanya lihat project assign)
- Filtering, keyword search, pagination (skip & limit)

### 3. Material Management
- CRUD Materi (`/materials`) → Admin/Dosen only
- Role-based access untuk GET list materi (Mahasiswa hanya lihat materi dari project assign)
- Filter berdasarkan `project_id`
- Pagination (skip & limit)

### 4. Logging & Error Handling
- Request logging middleware
- Global JSON error handler (`HTTPException`, `ValidationError`, generic Exception)
- Semua error dicatat di log file

### 5. Testing
- API tests menggunakan `pytest` & `TestClient`
- Semua endpoint CRUD dan role-access sudah teruji

---

## 🛠️ Teknologi
- Python 3.10
- FastAPI
- SQLAlchemy
- SQLite (default), bisa diganti PostgreSQL/MySQL
- Pydantic (Schemas & Validation)
- Pytest (API Testing)

---

## ⚡ Instalasi & Setup

1. **Clone repository**

```bash
git clone <repo-url>
cd pjblms-backend
```

2. **Buat virtual environment & install dependencies**

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

3. **Jalankan database migration**

```bash
python -m app.database
```

4. **Jalankan server FastAPI**

```bash
uvicorn app.main:app --reload
```

5. **Buka Doc API**

```bash
http://[IP_address]:8000/docs
```

---

## Struktur Project
```bash
app/
├── main.py            # Entry point FastAPI
├── database.py        # SQLAlchemy engine & session
├── models.py          # ORM models (User, Project, Material, Assignment)
├── schemas.py         # Pydantic schemas
├── auth.py            # JWT authentication, hashing, require_roles
├── routes/
│   ├── auth.py
│   ├── users.py
│   ├── projects.py
│   └── materials.py
├── middleware/
│   ├── log_requests.py
│   └── error_handler.py
├── logger.py          # Logging setup
└── tests/
    ├── test_auth.py
    ├── test_projects.py
    ├── test_materials.py
    ├── test_role_access.py
    └── utils.py
```

---

## Testing
```bash
pytest
```
* Semua API tests sudah pass ✅
* Unit test, integration test, load test → belum tersedia

---

## Konfigurasi untuk Production
* Gunakan **SECRET_KEY** & **DATABASE_URL** dari environment variable
* Gunakan reverse proxy (Nginx / Caddy)
* Gunakan process manager (e.g., Gunicorn, Uvicorn + Systemd / Supervisor)
* Backup database & monitoring

---

## Catatan
* Role-based GET list untuk Project & Material sudah diterapkan
* Logging sudah ada, tapi JSON global error handler wajib digunakan
* Frontend belum dibuat (Login/Register, Dashboard role-based, CRUD UI, token management)

---

## Kontributor
Septian Jauhariansyah