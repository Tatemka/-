import socket
import requests
import threading
import time
import urllib.parse

# === НАСТРОЙКИ ===
PORT_CYBERPI = 5051
PORT_OLD = 5050
# Твой локальный сервер ntfy
NTFY_URL = "ВАШ_СЕРВЕР/kotost-market" 

# === ОТПРАВКА УВЕДОМЛЕНИЙ ===
def send_notification(title, message):
    try:
        # Кодируем заголовок для безопасной передачи в URL (чтобы русские буквы не ломали latin-1)
        safe_title = urllib.parse.quote(title)
        
        response = requests.post(
            f"{NTFY_URL}?title={safe_title}",
            data=message.encode('utf-8'),
            headers={
                "Priority": "high",
                "Tags": "cat",
                "Content-Type": "text/plain; charset=utf-8"
            },
            timeout=5
        )
        if response.status_code == 200:
            print(f"[{time.strftime('%H:%M:%S')}] Уведомление отправлено: {message}")
        else:
            print(f"[ОШИБКА NTFY] Код {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ОШИБКА NTFY] {e}")

# === ОБРАБОТКА КЛИЕНТА ===
def handle_client(conn, addr):
    print(f"[+] Подключение от {addr}")
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        if data:
            print(f"[{time.strftime('%H:%M:%S')}] Получено: {data}")
            
            # Отправляем уведомление
            send_notification("КОТОСТЬ МАРКЕТ", data)
            
            # Записываем в простой текстовый лог
            with open("/home/dietpi/kotost_orders.log", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {data} (от {addr[0]})\n")

        conn.sendall(b"OK\n")
    except Exception as e:
        print(f"[ОШИБКА] {e}")
    finally:
        conn.close()

# === ЗАПУСК СЕРВЕРА ===
def run_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[✓] Сервер слушает порт {port}")
    
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f"[ОШИБКА СЕРВЕРА] {e}")

if __name__ == "__main__":
    print(f"[✓] Уведомления идут на {NTFY_URL}")
    
    # Запускаем два сервера в разных потоках
    threading.Thread(target=run_server, args=(PORT_CYBERPI,), daemon=True).start()
    threading.Thread(target=run_server, args=(PORT_OLD,), daemon=True).start()

    # Бесконечный цикл, чтобы программа не закрывалась
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Остановка сервера...")
