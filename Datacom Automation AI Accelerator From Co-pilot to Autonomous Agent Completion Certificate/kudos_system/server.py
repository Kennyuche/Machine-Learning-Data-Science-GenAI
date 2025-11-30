from flask import Flask, g, request, jsonify, render_template, session, redirect
import sqlite3
import os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(__file__), 'kudos.db')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS kudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_visible INTEGER NOT NULL DEFAULT 1,
            moderated_by INTEGER,
            moderated_at TEXT,
            reason_for_moderation TEXT
        )
    ''')
    db.commit()

    # Seed sample users if table empty
    r = query_db('SELECT COUNT(1) as c FROM users', one=True)
    if r and r['c'] == 0:
        cur.execute('INSERT INTO users (username, is_admin) VALUES (?, ?)', ('alice', 0))
        cur.execute('INSERT INTO users (username, is_admin) VALUES (?, ?)', ('bob', 0))
        cur.execute('INSERT INTO users (username, is_admin) VALUES (?, ?)', ('carol', 1))
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Flask 3 removed `before_first_request`; initialize DB at import time instead.
with app.app_context():
    init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/whoami')
def whoami():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'user': None})
    user = query_db('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,), one=True)
    if not user:
        return jsonify({'user': None})
    return jsonify({'user': {'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin'])}})


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id') or request.json and request.json.get('user_id')
    if not user_id:
        return redirect('/')
    user = query_db('SELECT id FROM users WHERE id = ?', (user_id,), one=True)
    if not user:
        return jsonify({'ok': False, 'error': 'user not found'}), 400
    session['user_id'] = user['id']
    return jsonify({'ok': True})


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'ok': True})


@app.route('/api/users')
def api_users():
    rows = query_db('SELECT id, username, is_admin FROM users ORDER BY username')
    users = [{'id': r['id'], 'username': r['username'], 'is_admin': bool(r['is_admin'])} for r in rows]
    return jsonify({'users': users})


@app.route('/api/kudos', methods=['GET', 'POST'])
def api_kudos():
    if request.method == 'GET':
        limit = int(request.args.get('limit', 20))
        rows = query_db('''
            SELECT k.id, k.sender_id, s.username as sender, k.recipient_id, r.username as recipient,
                   k.message, k.created_at, k.is_visible, k.moderated_by, k.moderated_at, k.reason_for_moderation
            FROM kudos k
            JOIN users s ON s.id = k.sender_id
            JOIN users r ON r.id = k.recipient_id
            WHERE k.is_visible = 1
            ORDER BY datetime(k.created_at) DESC
            LIMIT ?
        ''', (limit,))
        kudos = [dict(row) for row in rows]
        return jsonify({'kudos': kudos})

    # POST -> create kudos
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'ok': False, 'error': 'authentication required'}), 401
    data = request.get_json() or {}
    recipient_id = data.get('recipient_id')
    message = (data.get('message') or '').strip()
    if not recipient_id:
        return jsonify({'ok': False, 'error': 'recipient_id required'}), 400
    if not message:
        return jsonify({'ok': False, 'error': 'message required'}), 400
    if len(message) > 500:
        return jsonify({'ok': False, 'error': 'message too long (500 char limit)'}), 400
    if int(recipient_id) == int(user_id):
        return jsonify({'ok': False, 'error': 'cannot send kudos to yourself'}), 400

    # Check recipient exists
    recipient = query_db('SELECT id FROM users WHERE id = ?', (recipient_id,), one=True)
    if not recipient:
        return jsonify({'ok': False, 'error': 'recipient not found'}), 400

    # Spam/duplicate check: identical message to same recipient within last 60 seconds
    dup = query_db('''
        SELECT COUNT(1) as c FROM kudos
        WHERE sender_id = ? AND recipient_id = ? AND message = ?
        AND datetime(created_at) >= datetime('now','-60 seconds')
    ''', (user_id, recipient_id, message), one=True)
    if dup and dup['c'] > 0:
        return jsonify({'ok': False, 'error': 'duplicate submission detected; try again later'}), 429

    db = get_db()
    cur = db.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO kudos (sender_id, recipient_id, message, created_at) VALUES (?, ?, ?, ?)',
                (user_id, recipient_id, message, now))
    db.commit()
    kudos_id = cur.lastrowid
    row = query_db('''
        SELECT k.id, k.sender_id, s.username as sender, k.recipient_id, r.username as recipient, k.message, k.created_at
        FROM kudos k JOIN users s ON s.id=k.sender_id JOIN users r ON r.id=k.recipient_id WHERE k.id=?
    ''', (kudos_id,), one=True)
    return jsonify({'ok': True, 'kudos': dict(row)})


@app.route('/api/kudos/<int:kudos_id>/moderate', methods=['POST'])
def moderate_kudos(kudos_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'ok': False, 'error': 'authentication required'}), 401
    user = query_db('SELECT id, is_admin FROM users WHERE id = ?', (user_id,), one=True)
    if not user or not user['is_admin']:
        return jsonify({'ok': False, 'error': 'admin required'}), 403
    data = request.get_json() or {}
    action = data.get('action')
    reason = data.get('reason')
    db = get_db()
    cur = db.cursor()
    if action == 'hide':
        now = datetime.utcnow().isoformat()
        cur.execute('''UPDATE kudos SET is_visible=0, moderated_by=?, moderated_at=?, reason_for_moderation=? WHERE id=?''',
                    (user_id, now, reason, kudos_id))
        db.commit()
        return jsonify({'ok': True})
    elif action == 'delete':
        cur.execute('DELETE FROM kudos WHERE id = ?', (kudos_id,))
        db.commit()
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'error': 'unknown action'}), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
