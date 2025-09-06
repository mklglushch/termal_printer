import threading, socket
import sqlite3



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
            if byte == 46 or byte == 61:  #обхід крапки на початку чеку 
                i += 1
                continue
            else:
                try:
                    result.append(raw_data[i:i + 1].decode('cp866'))
                except UnicodeDecodeError:
                    result.append('?')
            i += 1
        else:
            i += 1
    return ''.join(result)


def new_folder(file_path, check_text, db_path="info.db"):
    with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()  # strip() прибере \n в кінці
    # 2. Підключаємось до бази (якщо немає - створиться)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. Створюємо таблицю, якщо вона ще не існує
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            zaklad TEXT PRIMARY KEY,
            check_text TEXT NOT NULL
        );
    """)

    # 4. Додаємо запис (наприклад, заклад можна передати параметром)
    cursor.execute("""
        INSERT INTO checks (zaklad, check_text)
        VALUES (?, ?)
        ON CONFLICT(zaklad) DO UPDATE SET check_text = excluded.check_text
        """, (first_line, check_text))
    
    

    # 5. Зберігаємо і закриваємо
    conn.commit()
    conn.close()


# отримання даних від принтера
def handle_printer(conn):
    """Обробка даних від принтера"""
    full_text = []

    while True:
        data = conn.recv(2048)
        if not data:
            break
        full_text.append(decode_esc_pos(data))  # декодований текст
        #raw_data_list.append(data)              # зберігаємо байти

    if full_text:
        check_text = ''.join(full_text)
        if check_text == "C":
            pass
        else:
            # Запис тексту
            with open("printer_checks.txt", "w", encoding='utf-8') as f:
                f.write(check_text)
                f.write("\n")
        
            new_folder("printer_checks.txt", check_text)
        





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