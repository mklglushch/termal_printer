import threading, socket



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


# отримання даних від принтера
def handle_printer(conn):
    """Обробка даних від принтера"""
    full_text = []
    raw_data_list = []

    while True:
        data = conn.recv(2048)
        if not data:
            break
        full_text.append(decode_esc_pos(data))  # декодований текст
        #raw_data_list.append(data)              # зберігаємо байти

    if full_text:
        check_text = ''.join(full_text)

        # Запис тексту
        with open("printer_checks.txt", "w", encoding='utf-8') as f:
            f.write(check_text)
            f.write("\n")
        # Запис сирих байтів
        # with open("printer_raw.bin", "wb") as f:
        #     for chunk in raw_data_list:
        #         f.write(chunk)





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