# Wage System (一线员工薪酬核算系统)

食品加工企业一线生产员工薪酬自动核算原型系统。

## Features

- 👥 Employee management (CRUD)
- 💰 Piece rate + hourly wage calculation
- 🏭 Production output tracking (semi-finished, inner sales, outer sales)
- ✅ Quality deduction tracking
- ⏰ Attendance management
- 🧮 Monthly wage calculation and reporting

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the system

**Windows:**
```bash
start.bat
```

**Manual:**
```bash
python app.py
```

Then visit: <ADDRESS_REMOVED>

## Tech Stack

- **Backend**: Python 3.13 + Flask 2.3
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Database**: SQLite 3 (file-based)
- **API**: RESTful design

## Project Structure

```
wage-system/
├── app.py          # Flask backend main app
├── pc-v6.html     # Frontend (single file, API-integrated)
├── start.bat       # Windows one-click launcher
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md
```

## Database Structure

System auto-creates `wage_system.db` with these tables:

- `employees` - Employee info
- `prices` - Price standards
- `semi_records` - Semi-finished output
- `inner_records` - Inner sales output
- `outer_records` - Outer sales output
- `quality_records` - Quality deductions
- `attendance` - Attendance records
- `wage_results` - Wage calculation results

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/employees` | GET/POST/PUT/DELETE | Employee management |
| `/api/prices` | GET | Price standards |
| `/api/semi` | GET/POST/DELETE | Semi-finished output |
| `/api/inner` | GET/POST/DELETE | Inner sales output |
| `/api/outer` | GET/POST/DELETE | Outer sales output |
| `/api/quality` | GET/POST/DELETE | Quality deductions |
| `/api/attendance` | GET/POST | Attendance records |
| `/api/wage-calc` | POST | Calculate wages |
| `/api/wage-results` | GET | Wage results |
| `/api/stats/dashboard` | GET | Dashboard stats |
| `/api/export` | GET | Export Excel (TODO) |

## Configuration

### Wage calculation rules

Current simplified logic:
- **Piece rate** = total output (kg) × unit price (yuan/kg)
- **Hourly wage** = attendance hours × 20 yuan/h
- **Total wage** = piece rate + hourly wage - quality deductions

> 💡 For production deployment, modify calculation logic in `app.py` lines 160-190.

## Todo

- [ ] Implement Excel export (need openpyxl)
- [ ] Add user role management
- [ ] Support multi-month history query
- [ ] Auto-generate pay slips
- [ ] Mobile responsive design

## License

MIT

---

⚡ Built with speed by FlashForge (闪造造)
