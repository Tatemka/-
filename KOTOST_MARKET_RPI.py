import socket
import requests
import threading
import time

PORT_CYBERPI = 5051
PORT_OLD = 5050
NTFY_TOPIC = "ВАШ NTFY_TOPIC"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_notification(title, message):
    try:
        response = requests.post(
            f"{NTFY_URL}?title={title}",
            data=message.encode('utf-8'),
            headers={"Priority": "high", "Tags": "cat"},
            timeout=5
        )
        print(f"[{time.strftime('%H:%M:%S')}] Уведомление отправлено: {message}")
    except Exception as e:
        print(f"[ОШИБКА] {e}")

def handle_client(conn, addr):
    print(f"[+] Подключение от {addr}")
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        if data:
            print(f"Получено: {data}")
            send_notification("КОТОСТЬ МАРКЕТ", data)
        conn.sendall(b"OK\n")
    except Exception as e:
        print(f"[ОШИБКА] {e}")
    finally:
        conn.close()

def run_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[✓] Сервер слушает порт {port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Запускаем два сервера в разных потоках
threading.Thread(target=run_server, args=(PORT_CYBERPI,), daemon=True).start()
threading.Thread(target=run_server, args=(PORT_OLD,), daemon=True).start()

# Бесконечный цикл, чтобы программа не закрывалась
while True:
    time.sleep(1)
