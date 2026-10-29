import event, cyberpi, time
import socket

@event.start
def on_start():
    cyberpi.console.clear()
    cyberpi.wifi.connect("YourBannyWrote_2.4G", "PINkerton26K")
    time.sleep(5)
    if cyberpi.wifi.is_connected():
        cyberpi.console.print("Готов!")
    else:
        cyberpi.console.print("Wi-Fi FAIL!")

@event.is_press('b')
def is_btn_press():
    cyberpi.console.print("Отправка...")
    cyberpi.audio.play('iron')
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("192.168.1.140", 5051))
        client.send("ЗАКАЗ КОТОСТИ".encode('utf-8'))
        cyberpi.console.print("OK!")
    except Exception as e:
        cyberpi.console.print("Err: " + str(e)) # Покажет текст ошибки
    finally:
        client.close()
