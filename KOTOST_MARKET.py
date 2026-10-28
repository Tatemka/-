import event, cyberpi, time
import socket

@event.start
def on_start():
    cyberpi.console.clear()
    cyberpi.wifi.connect("ВАШ WI-FI", "ВАШ ПАРОЛЬ")
    time.sleep(5)
    if cyberpi.wifi.is_connected():
        cyberpi.console.print("Готов!")
    else:
        cyberpi.console.print("Wi-Fi FAIL!")

@event.is_press('b')
def is_btn_press():
    cyberpi.console.print("Отправка...")
    cyberpi.audio.play('meow')
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("IP-АДРЕС СЕРВЕРА", ПОРТ СЕРВЕРА))
        client.send("ЗАКАЗ КОТОСТИ".encode('utf-8'))
        cyberpi.console.print("Отправлено!")
    except Exception as e:
        cyberpi.console.print("Ошибка отправки")
    finally:
        client.close()
