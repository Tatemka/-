from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import requests
import urllib.parse

app = Flask(__name__)

NTFY_URL = "http://192.168.1.140/kotost-market"
DB_PATH = "/home/dietpi/kotost.db"

# HTML-шаблон с тёмной темой и кнопками (Заказ и Очистка)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 КОТОСТЬ МАРКЕТ</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 900px; }
        h1 { color: #4d6bfe; text-align: center; font-size: 2.5rem; margin-bottom: 5px; text-shadow: 0 0 10px rgba(77, 107, 254, 0.3); }
        .subtitle { text-align: center; color: #a0a0a0; margin-bottom: 30px; font-size: 1.1rem; }
        .card { background-color: #1e1e1e; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); border: 1px solid #333; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 12px 15px; background-color: #2d2d2d; color: #fff; font-weight: 600; border-bottom: 2px solid #4d6bfe; }
        th:first-child { border-top-left-radius: 8px; }
        th:last-child { border-top-right-radius: 8px; }
        td { padding: 12px 15px; border-bottom: 1px solid #333; color: #b0b0b0; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background-color: #252525; color: #fff; }
        .order-text { color: #ffaa00; font-weight: bold; }
        .stats { margin-top: 20px; padding: 15px; background-color: #1e1e1e; border-radius: 12px; text-align: center; font-size: 1.2rem; border: 1px solid #333; }
        .stats span { color: #4d6bfe; font-weight: bold; font-size: 1.4rem; }
        
        .btn-group { display: flex; gap: 15px; justify-content: center; margin-top: 20px; flex-wrap: wrap; }
        .btn { display: inline-block; padding: 12px 24px; background-color: #4d6bfe; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; transition: background-color 0.2s; border: none; cursor: pointer; font-size: 1rem; }
        .btn:hover { background-color: #3b53cc; }
        .btn-order { background-color: #ffaa00; color: #121212; }
        .btn-order:hover { background-color: #e69900; }
        .btn-clear { background-color: #ff4444; }
        .btn-clear:hover { background-color: #cc0000; }
        
        @media (max-width: 600px) { h1 { font-size: 1.8rem; } th, td { padding: 8px; font-size: 0.9rem; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 КОТОСТЬ МАРКЕТ</h1>
        <div class="subtitle">Добро пожаловать на кухню богов</div>

        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Заказ</th>
                        <th>IP-адрес</th>
                        <th>Время</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in orders %}
                    <tr>
                        <td>#{{ order[0] }}</td>
                        <td class="order-text">{{ order[1] }}</td>
                        <td>{{ order[2] }}</td>
                        <td>{{ order[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="stats">
            Всего заказов: <span>{{ orders|length }}</span>
        </div>

        <div class="btn-group">
            <a href="/" class="btn">🔄 Обновить</a>
            <form action="/order" method="POST" style="margin: 0;">
                <button type="submit" class="btn btn-order">🛒 Заказать котость!</button>
            </form>
            <form action="/clear" method="POST" style="margin: 0;">
                <button type="submit" class="btn btn-clear" onclick="return confirm('Ты уверен, что хочешь очистить всю базу?');">🗑️ Очистить базу</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_PAGE, orders=orders)

@app.route('/order', methods=['POST'])
def make_order():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Считаем, сколько сейчас заказов
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    # Если уже 20 (или больше), полностью очищаем базу
    if count >= 20:
        cursor.execute("DELETE FROM orders")
        print("[БД] Лимит 20 заказов достигнут. База полностью очищена!")
    
    # Добавляем новый заказ
    cursor.execute("INSERT INTO orders (message, ip_address) VALUES (?, ?)", ("ЗАКАЗ С ВЕБА", request.remote_addr))
    conn.commit()
    conn.close()

    # Отправляем уведомление в ntfy
    try:
        safe_title = urllib.parse.quote("КОТОСТЬ МАРКЕТ")
        requests.post(
            f"{NTFY_URL}?title={safe_title}",
            data="ЗАКАЗ С ВЕБА".encode('utf-8'),
            headers={"Priority": "high", "Tags": "cat", "Content-Type": "text/plain; charset=utf-8"},
            timeout=5
        )
    except Exception as e:
        print(f"Ошибка отправки в ntfy: {e}")

    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_orders():
    """Полностью очищает базу данных по нажатию кнопки"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders")
    conn.commit()
    conn.close()
    print("[БД] База данных очищена вручную через веб-интерфейс.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
