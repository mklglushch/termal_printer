#перевірка чи підписаний користувач
def check_subscribe(user_id):
    #відкриваємо файл з усіма айді аби перевірити чи є наше айді в переліку підписаних
    with open("subscribet_ID.txt", "r", encoding='utf-8') as f:
            existing_ids = [line.strip() for line in f.readlines()]
            
    #якщо є то інформуємо киростувача
    if str(user_id) in existing_ids:
        return (
            "ℹ️ Ви вже підписані на отримання чеків.\n"
            "/print - отримати останній друкований чек \n"
            "/file - отримати файл чеку \n"
            "/unsub - для відписки від бота"
        )
    #якщо ні то підписуємо його натоновлення та додаємо айді в чат
    else:
        with open("subscribet_ID.txt", "a", encoding="utf-8") as f:
            f.write(str(user_id) + "\n")

        return (
            "✅ Ви підписалися на отримання чеків.\n"
            "/print - отримати останній друкований чек \n"
            "/file - отримати файл чеку \n"
            "/unsub - для відписки від бота"
        )
       
#видалення користувача з файлу підписок 
def delete_user(user_id, file_path):
    #отримуємо усі user_id з файлу
    with open(file_path, "r", encoding='utf-8') as f:
        lines = f.readlines()

    # Видаляємо chat_id, якщо він є в списку
    new_lines = [line for line in lines if line.strip() != str(user_id)]

    # Перезаписуємо файл без видаленого chat_id
    with open(file_path, 'w') as f:
        f.writelines(new_lines)