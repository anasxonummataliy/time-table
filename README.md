# 📅 Time Table — Dars Jadvali Tizimi

Universitetlar uchun dars jadvali boshqaruv tizimi. FastAPI backend + vanilla HTML/CSS/JS frontend.

---

## 🖥️ Preview

![Jadval ko'rinishi](https://i.imgur.com/placeholder.png)

> **Asosiy sahifa** — haftalik dars jadvali, filtr va tezkor qo'shish imkoniyati bilan.

---

## ✨ Imkoniyatlar

- **Dars jadvali** — haftalik ko'rinish, toq/juft hafta filtri
- **Guruhlar** — qo'shish, tahrirlash, o'chirish
- **O'qituvchilar** — kontakt ma'lumotlari bilan
- **Xonalar** — holat boshqaruvi (`active` / `maintenance` / `closed`)
- **Conflict detection** — bir vaqtda bir xona/o'qituvchi/guruhda ikki dars qo'yilishining oldini oladi
- **Tamir ogohlantirishlari** — tamir yoki yopiq xonadagi darslar jadvalda belgilanadi
- **Real-time backend status** — sidebar da API ulanish holati

---

## 🗂️ Loyiha tuzilmasi

```
time-table/
├── app/
│   ├── api/
│   │   ├── room.py          # Xonalar CRUD + status endpoint
│   │   ├── group.py         # Guruhlar CRUD
│   │   ├── teacher.py       # O'qituvchilar CRUD
│   │   └── schedule.py      # Jadval CRUD + conflict tekshiruvi
│   ├── database/
│   │   ├── models/
│   │   │   ├── room.py
│   │   │   ├── group.py
│   │   │   ├── teacher.py
│   │   │   └── schedule.py
│   │   ├── base.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── room.py
│   │   ├── group.py
│   │   ├── teacher.py
│   │   └── schedule.py
│   ├── core/
│   │   └── config.py
│   └── main.py
├── migrations/
│   └── versions/
│       └── add_room_status.py
├── migrate_room_status.py   # Bir martalik status migration
├── index.html               # Frontend (single-file)
├── .env
└── README.md
```

---

## ⚙️ O'rnatish

### Talablar

- Python 3.11+
- PostgreSQL 14+

### 1. Reponi klonlash

```bash
git clone https://github.com/username/time-table.git
cd time-table
```

### 2. Virtual muhit va paketlar

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. `.env` fayli

```env
PG_USER=postgres
PG_PASS=your_password
PG_HOST=localhost
PG_PORT=5432
PG_DB=timetable

SECRET_KEY=your_secret_key_here
```

### 4. Ma'lumotlar bazasini yaratish

```bash
# PostgreSQL da
createdb timetable

# Alembic migratsiyalari
alembic upgrade head
```

### 5. Agar bazada eski status qiymatlari bo'lsa (bir marta)

```bash
python migrate_room_status.py
```

### 6. Serverni ishga tushirish

```bash
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`  
Swagger docs: `http://127.0.0.1:8000/docs`

### 7. Frontend

`index.html` faylini brauzerda oching — backend avtomatik ulanadi.

---

## 📡 API Endpointlar

### Guruhlar
| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/api/groups/` | Barcha guruhlar |
| `POST` | `/api/groups/` | Yangi guruh |
| `PATCH` | `/api/groups/{id}` | Guruhni tahrirlash |
| `DELETE` | `/api/groups/{id}` | Guruhni o'chirish |

### O'qituvchilar
| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/api/teachers/` | Barcha o'qituvchilar |
| `POST` | `/api/teachers/` | Yangi o'qituvchi |
| `PATCH` | `/api/teachers/{id}` | Tahrirlash |
| `DELETE` | `/api/teachers/{id}` | O'chirish |

### Xonalar
| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/api/rooms/` | Barcha xonalar |
| `POST` | `/api/rooms/` | Yangi xona |
| `PATCH` | `/api/rooms/{id}` | Xonani tahrirlash |
| `PATCH` | `/api/rooms/{id}/status` | Faqat holat o'zgartirish |
| `DELETE` | `/api/rooms/{id}` | O'chirish |

### Jadval
| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/api/schedules/` | Barcha darslar (filter: `group_id`, `teacher_id`, `room_id`, `week_type`) |
| `POST` | `/api/schedules/` | Yangi dars (conflict tekshiruvi bilan) |
| `PATCH` | `/api/schedules/{id}` | Darsni tahrirlash |
| `DELETE` | `/api/schedules/{id}` | O'chirish |

---

## 🏷️ Xona holatlari

| Qiymat | Ko'rinish | Ma'no |
|--------|-----------|-------|
| `active` | ✅ Faol | Dars o'tkazish mumkin |
| `maintenance` | 🔧 Tamirlash | Vaqtincha yopiq, jadvalda ogohlantirish chiqadi |
| `closed` | 🔒 Yopiq | Dars qo'yish bloklangan |

---

## 🔒 Conflict Detection

Jadval qo'shishda quyidagilar tekshiriladi:

- **Xona konflikti** — bir vaqtda bir xonada ikki dars
- **O'qituvchi konflikti** — bir vaqtda bir o'qituvchi ikki darsda
- **Guruh konflikti** — bir vaqtda bir guruh ikki darsda
- **Hafta turi** — `null` (har hafta) toq va juft hafta bilan ham konfliktga tushadi

---

## 🛠️ Texnologiyalar

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async REST API
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) — async ORM
- [asyncpg](https://github.com/MagicStack/asyncpg) — PostgreSQL driver
- [Pydantic v2](https://docs.pydantic.dev/) — validatsiya
- [Alembic](https://alembic.sqlalchemy.org/) — migratsiyalar

**Frontend**
- Vanilla HTML / CSS / JavaScript (single file, zero dependencies)
- [Syne](https://fonts.google.com/specimen/Syne) + [DM Mono](https://fonts.google.com/specimen/DM+Mono) — fontlar

---

## 📝 Litsenziya

MIT
