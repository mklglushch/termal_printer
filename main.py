from flask import Flask, request, jsonify
import socket
import threading
import requests
import time

app = Flask(__name__)

TOKEN = '7956558016:AAHD-lrL5s5IHQ7X0u1zCZ2z0OmvkH8eDto'
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def set_webhook():
    new_webhook_url = "https://ff67648774fc.ngrok-free.app/bot"  # Замініть на нову адресу
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={new_webhook_url}"
    )
    print("Webhook setup result:", response.json())

def decode_esc_pos(raw_data):
    result = []
    i = 0
    length = len(raw_data)

    while i < length:
        byte = raw_data[i]
        if byte == 0x1B and i + 1 < length:
            i += 2
            continue
        elif byte == 0x1D and i + 1 < length:
            i += 2
            continue
        elif byte == 0x0A:
            result.append('\n')
            i += 1
        elif byte == 0x0D:
            if i + 1 < length and raw_data[i + 1] == 0x0A:
                result.append('\n')
                i += 2
            else:
                result.append('\n')
                i += 1
        elif 0x20 <= byte <= 0xFF:
            try:
                result.append(raw_data[i:i + 1].decode('cp866'))
            except UnicodeDecodeError:
                result.append('?')
            i += 1
        else:
            i += 1
    return ''.join(result)


def send_message(chat_id, text):
    """Надсилання повідомлення в Telegram"""
    try:
        requests.post(TELEGRAM_URL, json={'chat_id': chat_id, 'text': text})
    except Exception as e:
        print(f"Помилка відправки: {e}")

def handle_printer(conn):
    """Обробка даних від принтера"""
    full_text = []
    while True:
        data = conn.recv(2048)
        if not data:
            break
        full_text.append(decode_esc_pos(data))
    
    if full_text:
        check_text = ''.join(full_text)
        with open("printer_checks.txt", "w", encoding='utf-8') as f:
            f.write(check_text)
        
        # Надсилання всім підписаним користувачам
        try:
            with open("subscribet_ID.txt", "r", encoding='utf-8') as f:
                for chat_id in f.read().splitlines():
                    if chat_id.strip():
                        send_message(chat_id.strip(), f"🖨 Новий чек:\n\n{check_text}")
                        print("надіслано чек")
        except FileNotFoundError:
            pass

def printer_server():
    """Сервер для прийому даних з принтера"""
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 9100))
        s.listen()
        print("Сервер принтера готовий до підключень...")
        
        while True:
            try:
                conn, addr = s.accept()
                print(f"Підключено принтер: {addr[0]}")
                threading.Thread(target=handle_printer, args=(conn,)).start()
            except Exception as e:
                print(f"Помилка: {e}")
    

def send_recepient_file(chat_id, file_path):
    TELEGRAM_URL_DOC = f"https://api.telegram.org/bot{TOKEN}"
    with open(file_path, 'rb') as file:
            response = requests.post(
                f"{TELEGRAM_URL_DOC}/sendDocument",
                files={'document': file},
                data={'chat_id': chat_id}
            )
            return response.json()

    

@app.route('/bot', methods=['POST'])
def bot():
    """Обробка команд Telegram бота"""
    data = request.json
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '').strip()

    if not chat_id:
        return jsonify({'ok': False})

    if text == "/start":
        # Перевіряємо, чи вже є такий chat_id у файлі
        already_subscribed = False
        try:
            with open("subscribet_ID.txt", "r", encoding='utf-8') as f:
                existing_ids = [line.strip() for line in f.readlines()]
                if str(chat_id) in existing_ids:
                    already_subscribed = True
        except FileNotFoundError:
            pass
        
        if not already_subscribed:
            with open("subscribet_ID.txt", "a", encoding='utf-8') as f:
                f.write(f"{chat_id}\n")
            send_message(chat_id, "✅ Ви підписані на отримання чеків.")
        else:
            send_message(chat_id, "ℹ️ Ви вже підписані на отримання чеків.")
    elif text == "/print":
        try:
            with open("printer_checks.txt", "r", encoding='utf-8') as f:
                last_check = f.read()
            send_message(chat_id, last_check if last_check else "Чеків ще немає")
        except FileNotFoundError:
            send_message(chat_id, "Чеків ще немає")
    elif text == "/file":
        file_path = "printer_checks.txt"  # Шлях до вашого файлу
        send_recepient_file(chat_id, file_path)
    else:
        send_message(chat_id, "/start - ініціалізація бота \n/print - отримати останній друкований чек \n/file - отримати файл чеку")

    return jsonify({'ok': True})

if __name__ == '__main__':
    print("Запуск системи...")
    set_webhook()  # Додайте цей рядок
    threading.Thread(target=printer_server, daemon=True).start()
    app.run(host='0.0.0.0', port=12345)