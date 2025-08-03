from flask import Flask, request, jsonify
import socket
import threading
import requests
import time

app = Flask(__name__)

TOKEN = '7956558016:AAHD-lrL5s5IHQ7X0u1zCZ2z0OmvkH8eDto'
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

#ставимо вебхук в разі заміни посилання на ngrok
def set_webhook():
    new_webhook_url = "https://6d897a75db67.ngrok-free.app/bot"  # Замінити на нову адресу
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={new_webhook_url}"
    )
    print("Webhook setup result:", response.json())


#дешифратор коду
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



#універсальна відправка повідомлень
def send_message(chat_id, text):
    """Надсилання повідомлення в Telegram"""
    try:
        requests.post(TELEGRAM_URL, json={
            'chat_id': chat_id,
            'text': text,
        })
    except Exception as e:
        print(f"Помилка відправки: {e}")
        
        
def send_last_recepient(chat_id, text):
    """Надсилання повідомлення в Telegram"""
    try:
        requests.post(TELEGRAM_URL, json={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        })
    except Exception as e:
        print(f"Помилка відправки: {e}")



#отримання данних від принтеру
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
            with open("subscribet_ID.txt", "r", encoding='utf-8') as f:# тут треба замінити щоб відправлялося лише підписаним користувачам
                for chat_id in f.read().splitlines():
                    if chat_id.strip():
                        send_last_recepient(chat_id.strip(), f"🖨 Новий чек:\n\n```\n{check_text}\n```")
                        print("надіслано чек")
        except FileNotFoundError:
            pass



#Сервер для прийому даних з принтера
def printer_server():
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
    


#надсилання останнього чеку файлом
def send_recepient_file(chat_id, file_path):
    TELEGRAM_URL_DOC = f"https://api.telegram.org/bot{TOKEN}"
    with open(file_path, 'rb') as file:
            response = requests.post(
                f"{TELEGRAM_URL_DOC}/sendDocument",
                files={'document': file},
                data={'chat_id': chat_id}
            )
            return response.json()
        

def insub(chat_id, file_path):
    # Зчитуємо всі рядки з файлу
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Видаляємо chat_id, якщо він є в списку
    new_lines = [line for line in lines if line.strip() != str(chat_id)]

    # Перезаписуємо файл без видаленого chat_id
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    
#Обробка команд Telegram бота
@app.route('/bot', methods=['POST'])
def bot():
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
            send_message(chat_id, "✅ Ви підписані на отримання чеків. \n/print - отримати останній друкований чек \n/file - отримати файл чеку \n/unsub - для відписки від бота")
        else:
            send_message(chat_id, "ℹ️ Ви вже підписані на отримання чеків.\n/print - отримати останній друкований чек \n/file - отримати файл чеку \n/unsub - для відписки від бота")
    #друк чеків по команді
    elif text == "/print":
        try:
            with open("printer_checks.txt", "r", encoding='utf-8') as f:
                last_check = f.read()
            if last_check:
                send_last_recepient(chat_id, f"🖨 Останній чек:\n\n```\n{last_check}\n```")
        except FileNotFoundError:
            send_message(chat_id, "Чеків ще немає")
    #друк чеків з файлу
    elif text == "/file":
        file_path = "printer_checks.txt"  # Шлях до вашого файлу
        send_recepient_file(chat_id, file_path)
    elif text == "/unsub":
        insub(chat_id, "subscribet_ID.txt")
        send_message(chat_id, "Ви успішно відписалися від отримання нових чеків, для підписки натисніть /start")
    else:
        send_message(chat_id, "/start - ініціалізація бота \n/print - отримати останній друкований чек \n/file - отримати файл чеку \n/unsub - для відписки від бота")

    return jsonify({'ok': True})

if __name__ == '__main__':
    print("Запуск системи...")
    set_webhook()  # Додайте цей рядок
    threading.Thread(target=printer_server, daemon=True).start()
    app.run(host='0.0.0.0', port=12345)