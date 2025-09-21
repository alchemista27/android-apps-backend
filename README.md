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
