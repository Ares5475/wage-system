# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)
DB = 'wage_system.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB):
        os.remove(DB)
    conn = get_db()
    c = conn.cursor()
    c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY AUTOINCREMENT, emp_code TEXT UNIQUE, name TEXT, section TEXT, emp_type TEXT, hire_date TEXT, status TEXT DEFAULT "在职", created_at TEXT)')
    c.execute('CREATE TABLE prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, section TEXT, unit_price REAL, unit TEXT)')
    c.execute('CREATE TABLE semi_records (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, emp_code TEXT, product_name TEXT, weight REAL, created_at TEXT)')
    c.execute('CREATE TABLE inner_records (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, emp_code TEXT, product_name TEXT, weight REAL, created_at TEXT)')
    c.execute('CREATE TABLE outer_records (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, emp_code TEXT, product_name TEXT, weight REAL, created_at TEXT)')
    c.execute('CREATE TABLE quality_records (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, emp_code TEXT, description TEXT, deduct_count INTEGER, created_at TEXT)')
    c.execute('CREATE TABLE attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, emp_code TEXT, hours REAL, note TEXT, created_at TEXT)')
    c.execute('CREATE TABLE wage_results (id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT, emp_code TEXT, name TEXT, section TEXT, emp_type TEXT, total_output REAL, piece_wage REAL, attendance_hours REAL, hourly_wage REAL, quality_deduct INTEGER, total_wage REAL, approved INTEGER DEFAULT 0, created_at TEXT)')
    emps = [('E001','张伟','外包','计件','2025-01-15'),('E002','李强','外包','计件','2025-03-01'),('E003','王明','内包','计件','2025-02-20'),('E004','刘芳','内包','计件','2025-04-10'),('E005','陈刚','烘烤','计件','2025-01-08'),('E006','赵丽','外包','计件','2025-05-12'),('E007','孙伟','内包','计件','2025-03-25'),('T001','周杰','内包','计时','2025-01-10'),('T002','吴敏','外包','计时','2025-02-15'),('T003','郑华','烘烤','计时','2025-01-20')]
    c.executemany('INSERT INTO employees (emp_code,name,section,emp_type,hire_date,status) VALUES (?,?,?,?,?,"在职")', emps)
    prices = [('辣条基料','外包',2.50,'kg'),('辣条成品A','外包',1.80,'kg'),('内包4根','内包',1.20,'中包'),('内包5根','内包',1.00,'中包'),('烘烤半成品','烘烤',3.00,'kg')]
    c.executemany('INSERT INTO prices (product_name,section,unit_price,unit) VALUES (?,?,?,?)', prices)
    conn.commit()
    conn.close()
    print('DB OK')

@app.route('/')
def index():
    return send_from_directory('.', 'pc-v6.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/employees', methods=['GET','POST','PUT','DELETE'])
def employees_api():
    conn = get_db()
    if request.method == 'GET':
        rows = conn.execute('SELECT * FROM employees WHERE status="在职" ORDER BY emp_code').fetchall()
        conn.close()
        return jsonify({'success':True,'data':[dict(r) for r in rows]})
    d = request.get_json(silent=True) or {}
    if request.method == 'POST':
        try:
            conn.execute('INSERT INTO employees (emp_code,name,section,emp_type,hire_date,status) VALUES (?,?,?,?,?,"在职")', (d['emp_code'],d['name'],d['section'],d['emp_type'],d.get('hire_date','')))
            conn.commit(); conn.close(); return jsonify({'success':True})
        except Exception as e:
            conn.close(); return jsonify({'success':False,'message':str(e)}), 400
    if request.method == 'PUT':
        conn.execute('UPDATE employees SET name=?, section=?, emp_type=?, hire_date=? WHERE emp_code=?', (d['name'],d['section'],d['emp_type'],d.get('hire_date',''),d['emp_code']))
        conn.commit(); conn.close(); return jsonify({'success':True})
    if request.method == 'DELETE':
        code = request.args.get('code') or d.get('emp_code','')
        conn.execute('UPDATE employees SET status="离职" WHERE emp_code=?', (code,))
        conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/prices', methods=['GET'])
def prices_api():
    conn = get_db()
    rows = conn.execute('SELECT * FROM prices ORDER BY section,product_name').fetchall()
    conn.close()
    return jsonify({'success':True,'data':[dict(r) for r in rows]})

def _get_records(conn, table, date_from, date_to, emp_code):
    sql = f'SELECT * FROM {table} WHERE 1=1'
    args = []
    if date_from: sql += ' AND date>=?'; args.append(date_from)
    if date_to: sql += ' AND date<=?'; args.append(date_to)
    if emp_code: sql += ' AND emp_code=?'; args.append(emp_code)
    sql += ' ORDER BY date DESC LIMIT 200'
    return conn.execute(sql, args).fetchall()

@app.route('/api/semi', methods=['GET','POST','DELETE'])
def semi_api():
    conn = get_db()
    if request.method == 'GET':
        rows = _get_records(conn, 'semi_records', request.args.get('date_from',''), request.args.get('date_to',''), request.args.get('emp_code',''))
        conn.close(); return jsonify({'success':True,'data':[dict(r) for r in rows]})
    if request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO semi_records (date,emp_code,product_name,weight,created_at) VALUES (?,?,?,?,?)', (d['date'],d['emp_code'],d['product_name'],d['weight'],datetime.now().isoformat()))
        conn.commit(); conn.close(); return jsonify({'success':True})
    if request.method == 'DELETE':
        rid = request.args.get('id',''); conn.execute('DELETE FROM semi_records WHERE id=?', (rid,)); conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/inner', methods=['GET','POST','DELETE'])
def inner_api():
    conn = get_db()
    if request.method == 'GET':
        rows = _get_records(conn, 'inner_records', request.args.get('date_from',''), request.args.get('date_to',''), request.args.get('emp_code',''))
        conn.close(); return jsonify({'success':True,'data':[dict(r) for r in rows]})
    if request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO inner_records (date,emp_code,product_name,weight,created_at) VALUES (?,?,?,?,?)', (d['date'],d['emp_code'],d['product_name'],d['weight'],datetime.now().isoformat()))
        conn.commit(); conn.close(); return jsonify({'success':True})
    if request.method == 'DELETE':
        rid = request.args.get('id',''); conn.execute('DELETE FROM inner_records WHERE id=?', (rid,)); conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/outer', methods=['GET','POST','DELETE'])
def outer_api():
    conn = get_db()
    if request.method == 'GET':
        rows = _get_records(conn, 'outer_records', request.args.get('date_from',''), request.args.get('date_to',''), request.args.get('emp_code',''))
        conn.close(); return jsonify({'success':True,'data':[dict(r) for r in rows]})
    if request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO outer_records (date,emp_code,product_name,weight,created_at) VALUES (?,?,?,?,?)', (d['date'],d['emp_code'],d['product_name'],d['weight'],datetime.now().isoformat()))
        conn.commit(); conn.close(); return jsonify({'success':True})
    if request.method == 'DELETE':
        rid = request.args.get('id',''); conn.execute('DELETE FROM outer_records WHERE id=?', (rid,)); conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/quality', methods=['GET','POST','DELETE'])
def quality_api():
    conn = get_db()
    if request.method == 'GET':
        rows = _get_records(conn, 'quality_records', request.args.get('date_from',''), request.args.get('date_to',''), request.args.get('emp_code',''))
        conn.close(); return jsonify({'success':True,'data':[dict(r) for r in rows]})
    if request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO quality_records (date,emp_code,description,deduct_count,created_at) VALUES (?,?,?,?,?)', (d['date'],d['emp_code'],d.get('description',''),d.get('deduct_count',1),datetime.now().isoformat()))
        conn.commit(); conn.close(); return jsonify({'success':True})
    if request.method == 'DELETE':
        rid = request.args.get('id',''); conn.execute('DELETE FROM quality_records WHERE id=?', (rid,)); conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/attendance', methods=['GET','POST'])
def attendance_api():
    conn = get_db()
    if request.method == 'GET':
        date_from = request.args.get('date_from','')
        date_to = request.args.get('date_to','')
        sql = 'SELECT * FROM attendance WHERE 1=1'
        args = []
        if date_from: sql += ' AND date>=?'; args.append(date_from)
        if date_to: sql += ' AND date<=?'; args.append(date_to)
        sql += ' ORDER BY date DESC LIMIT 500'
        rows = conn.execute(sql, args).fetchall()
        conn.close(); return jsonify({'success':True,'data':[dict(r) for r in rows]})
    if request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO attendance (date,emp_code,hours,note,created_at) VALUES (?,?,?,?,?)', (d['date'],d['emp_code'],d['hours'],d.get('note',''),datetime.now().isoformat()))
        conn.commit(); conn.close(); return jsonify({'success':True})

@app.route('/api/wage-calc', methods=['POST'])
def wage_calc_api():
    d = request.get_json()
    month = d.get('month','')
    if not month: return jsonify({'success':False,'message':'请选择月份'}), 400
    conn = get_db()
    employees = conn.execute('SELECT * FROM employees WHERE status="在职"').fetchall()
    prices = {p['product_name']: p['unit_price'] for p in conn.execute('SELECT * FROM prices').fetchall()}
    semi_rows = conn.execute('SELECT * FROM semi_records WHERE date LIKE ?', (month+'%',)).fetchall()
    inner_rows = conn.execute('SELECT * FROM inner_records WHERE date LIKE ?', (month+'%',)).fetchall()
    outer_rows = conn.execute('SELECT * FROM outer_records WHERE date LIKE ?', (month+'%',)).fetchall()
    quality_rows = conn.execute('SELECT * FROM quality_records WHERE date LIKE ?', (month+'%',)).fetchall()
    att_rows = conn.execute('SELECT * FROM attendance WHERE date LIKE ?', (month+'%',)).fetchall()
    def sum_weight(rows, ec):
        return sum(r['weight'] for r in rows if r['emp_code'] == ec)
    def sum_hours(rows, ec):
        return sum(r['hours'] for r in rows if r['emp_code'] == ec)
    def sum_quality(rows, ec):
        return sum(r['deduct_count'] for r in rows if r['emp_code'] == ec)
    results = []
    for e in employees:
        ec = e['emp_code']
        total_weight = sum_weight(semi_rows, ec) + sum_weight(inner_rows, ec) + sum_weight(outer_rows, ec)
        piece_wage = 0
        for r in semi_rows:
            if r['emp_code'] == ec: piece_wage += (r['weight'] or 0) * prices.get(r['product_name'], 0)
        for r in inner_rows:
            if r['emp_code'] == ec: piece_wage += (r['weight'] or 0) * prices.get(r['product_name'], 0)
        for r in outer_rows:
            if r['emp_code'] == ec: piece_wage += (r['weight'] or 0) * prices.get(r['product_name'], 0)
        att_hours = sum_hours(att_rows, ec)
        hourly_rate = 20 if e['emp_type'] == '计时' else 0
        hourly_wage = round(att_hours * hourly_rate * 100) / 100
        if e['emp_type'] == '计件': wage = piece_wage
        else: wage = hourly_wage
        quality_deduct = sum_quality(quality_rows, ec) * 50
        total_wage = max(0, round((wage - quality_deduct) * 100) / 100)
        results.append({'emp_code':ec,'name':e['name'],'section':e['section'],'emp_type':e['emp_type'],'total_output':round(total_weight*100)/100,'piece_wage':round(piece_wage*100)/100,'attendance_hours':round(att_hours*100)/100,'hourly_wage':hourly_wage,'quality_deduct':quality_deduct,'total_wage':total_wage})
    conn.execute('DELETE FROM wage_results WHERE month=?', (month,))
    for r in results:
        conn.execute('INSERT INTO wage_results (month,emp_code,name,section,emp_type,total_output,piece_wage,attendance_hours,hourly_wage,quality_deduct,total_wage,approved,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?)', (month,r['emp_code'],r['name'],r['section'],r['emp_type'],r['total_output'],r['piece_wage'],r['attendance_hours'],r['hourly_wage'],r['quality_deduct'],r['total_wage'],datetime.now().isoformat()))
    conn.commit(); conn.close()
    return jsonify({'success':True,'results':results})

@app.route('/api/wage-results', methods=['GET'])
def wage_results_api():
    month = request.args.get('month','')
    conn = get_db()
    if month: rows = conn.execute('SELECT * FROM wage_results WHERE month=? ORDER BY total_wage DESC', (month,)).fetchall()
    else: rows = conn.execute('SELECT * FROM wage_results ORDER BY created_at DESC LIMIT 100').fetchall()
    conn.close()
    return jsonify({'success':True,'data':[dict(r) for r in rows]})

@app.route('/api/stats/dashboard', methods=['GET'])
def stats_dashboard():
    conn = get_db()
    emp_count = conn.execute('SELECT COUNT(*) as c FROM employees WHERE status="在职"').fetchone()['c']
    month = datetime.now().strftime('%Y-%m')
    semi_w = conn.execute('SELECT SUM(weight) as s FROM semi_records WHERE date LIKE ?', (month+'%',)).fetchone()['s'] or 0
    inner_w = conn.execute('SELECT SUM(weight) as s FROM inner_records WHERE date LIKE ?', (month+'%',)).fetchone()['s'] or 0
    outer_w = conn.execute('SELECT SUM(weight) as s FROM outer_records WHERE date LIKE ?', (month+'%',)).fetchone()['s'] or 0
    month_output = semi_w + inner_w + outer_w
    wage_rows = conn.execute('SELECT AVG(total_wage) as a FROM wage_results WHERE month=?', (month,)).fetchone()
    avg_wage = wage_rows['a'] or 0
    quality_count = conn.execute('SELECT COUNT(*) as c FROM quality_records WHERE date LIKE ?', (month+'%',)).fetchone()['c']
    top = conn.execute('''SELECT e.name, e.section, (COALESCE(s.w,0)+COALESCE(i.w,0)+COALESCE(o.w,0)) as total FROM employees e LEFT JOIN (SELECT emp_code, SUM(weight) as w FROM semi_records WHERE date LIKE ? GROUP BY emp_code) s ON e.emp_code=s.emp_code LEFT JOIN (SELECT emp_code, SUM(weight) as w FROM inner_records WHERE date LIKE ? GROUP BY emp_code) i ON e.emp_code=i.emp_code LEFT JOIN (SELECT emp_code, SUM(weight) as w FROM outer_records WHERE date LIKE ? GROUP BY emp_code) o ON e.emp_code=o.emp_code WHERE e.status="在职" ORDER BY total DESC LIMIT 5''', (month+'%',month+'%',month+'%')).fetchall()
    conn.close()
    return jsonify({'success':True,'data':{'emp_count':emp_count,'month_output':round(month_output*100)/100,'avg_wage':round(avg_wage*100)/100,'quality_count':quality_count,'top_employees':[{'name':r['name'],'section':r['section'],'total':r['total']} for r in top if r['total']]}})

if __name__ == '__main__':
    init_db()
    print('Server starting on <ADDRESS_REMOVED>')
