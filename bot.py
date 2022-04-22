import telebot
import config
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

bot = telebot.TeleBot(config.TOKEN)


def have_access(telegram_id: int) -> bool:
    connection = psycopg2.connect(
        database=config.DATABASE,
        user=config.USER,
        password=config.PASSWORD,
        host=config.HOST,
        port=config.PORT
    )
    cursor = connection.cursor()
    cursor.execute(f'SELECT tg_id FROM tg_access WHERE tg_id={telegram_id};')
    result = bool(cursor.fetchall())
    connection.close()

    return result


@bot.message_handler(commands=['getall'])
def get(message):
    send = bot.send_message(message.chat.id,'Какую информацию Вы хотите получить? \n1) Больницу(сотрудники, пациенты,, лаборатории, общая информация) \n2) О враче(пациенте, контакты, место работы)\n3) О лаборатории(не ебу че это за залупа ваще, хз че с ней делать)\n4) О пациенте(лежит ли стационаре, в какой палате, диагноз, результаты анализов, лечущий врач, номер больницы)\n  5) О палате(персонал, больные)')
    bot.register_next_step_handler(send, get_category)


def get_category(message):

    match message.text:

        case '1':
            answer_text = 'Выберите информацию о чем Вы хотите получить?\n1) Персонал палат\n2) Врачи\n3) Все сотрудники\n4) Пациенты\n5) Лаборатории\n6) Общая информация'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, get_hospital_info)

        case '2':
            answer_text = 'Чтобы получить данные врача, введите ФИО'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, search_write)

        case '3':
            answer_text = 'Чтобы получить данные лаборатории я хуй знает че сделать надо....'
            # пока похуй потом сделаю

        case '4':
            answer_text = 'Чтобы получить данные пациента, введите ФИО'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, search_write)

        case '5':
            answer_text = 'Чтобы получить данные о палате, введите номер палаты и номер/адрес больницы'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, search_write)
        case _:
            bot.send_message(message.chat.id, 'Все сначала, ебанат \nИз списка выбери, сука')


def get_constraint_hospital(message):
    match message.text:
        case '1':
            send = bot.send_message(message.chat.id, 'Для того, чтобы получить персонал, отправьте сообщение в следующем формате\n*номер больницы*(или адрес); *номер палаты*')
            bot.register_next_step_handler(send, get_hospital_room_staff)


def get_hospital_room_staff(message):
    content = message.text.split(';')
    if len(content) == 1:
        if len(content[0]) > 3:
            req = f'SELECT * FROM staff'
        else:
            hospital_number = content[0]


def get_hospital_info(message):
    connection = psycopg2.connect(
        database=config.DATABASE,
        user=config.USER,
        password=config.PASSWORD,
        host=config.HOST,
        port=config.PORT
    )
    cursor = connection.cursor()
    match message.text:
        case '6':
            answer = ''
            if message.text == '*':
                cursor.execute('SELECT * FROM hospital;')
                hospitals = cursor.fetchall()
                print(hospitals)
                for hospital in hospitals:
                    answer += f'{hospitals.index(hospital)+1}) №{hospital[0]}, {hospital[1]}\n'
                bot.send_message(message.chat.id, answer)
            connection.close()


def search_write(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['add'])
def add_write(message):

    if have_access(message.chat.id):
        send = bot.send_message(message.chat.id,
                        '''Что Вы хотите добавить?\n1) Больницу\n2) Палату\n3) Врача\n4) Лабораторию\n5) Пациента\n6) Чьи-то анализы\n7) Персонал палаты\n8) Чей-то диагноз"''')
        bot.register_next_step_handler(send, add_category)
    else:
        bot.send_message(message.chat.id, "У вас нет прав для редактирования БД")


def add_category(message):

    match message.text:

        case '1':
            answer_text = 'Чтобы добавить данные о больнице, необходимо написать их в следующем формате:\n*номер больницы*; *адрес*'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_hospital)
        case '2':
            answer_text = 'Чтобы добавить данные о палате, необходимо написать их в следующем формате:\n*номер больницы*(адрес); *номер палаты*'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_hospital_room)
        case '3':
            answer_text = 'Чтобы добавить врача, необходимо написать их в следующем формате:\n*имя*; *отчество*; *фамилия*; *страна рождения*; *электронная почта*; *номер телефона*;\n*должность*; *дата рождения*; *место работы(номер\адрес больницы)*'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_doctor)
        case '4':
            answer_text = 'Не ебу че такое ебанные лаборатории'
            bot.send_message(message.chat.id, answer_text)
        case '5':
            answer_text = 'Чтобы добавить пациента, необходимо написать их в следующем формате:\n*имя*; *отчество*; *фамилия*; *место проживания*; *электронная почта*; *номер телефона*;\n*дата рождения*; *фамилия и инициалы лечащего врача*; *номер больницы(адрес больницы)*; *номер палаты(если нет "-" )*'
            send = bot.send_message(message.chat.id, add_patient)
            bot.register_next_step_handler(send, add_doctor)
        case _:
            bot.send_message(message.chat.id, 'Все сначала, ебанат \nИз списка выбери, сука')


def add_hospital(message):
    try:
        number, address = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Ну, сука, ну и дебил, я хуею. ТЫ ДОЛЖЕН БЫЛ НАПИСАТЬ ДАННЫЕ КАК УКАЗАНО ВЫШЕ!')
    else:
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOST,
            port=config.PORT
        )
        cursor = connection.cursor()
        try:
            cursor.execute(f'INSERT INTO hospital (id, address) VALUES ({number}, \'{address.strip()}\')')
        except UniqueViolation:
            bot.send_message(message.chat.id, "Больница с таким номером уже находится в базе!")
        else:
            connection.commit()
            bot.send_message(message.chat.id, f'Запись была успешна создана!')
        connection.close()


def add_hospital_room(message):
    try:
        hospital_number, room_number = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Сообщение в неправильном формате!')
    else:
        request = f'INSERT INTO hospital_room (hospital_id, number) VALUES ({hospital_number}, {room_number});'
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOST,
            port=config.PORT
        )
        cursor = connection.cursor()
        try:
            cursor.execute(request)
        except ForeignKeyViolation:
            bot.send_message(message.chat.id, "Больницы с таким номером не существует в базе!")
        except UniqueViolation:
            bot.send_message(message.chat.id, "Палата с таким номером уже существует!")
        else:
            connection.commit()
            bot.send_message(message.chat.id, 'Палата успешно добавлена.')
            connection.close()


def add_doctor(message):
    try:
        first_name, middle_name, last_name, country, email, phone, position, birthdate, hospital_id = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Неверный формат сообщения!')
    else:
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOST,
            port=config.PORT
        )
        cursor = connection.cursor()

        if len(hospital_id) > 3:
            cursor.execute(f'SELECT id FROM hospital WHERE address = \'{hospital_id.strip()}\' ')
            try:
                hospital_id = cursor.fetchall()[0][0]
                print(hospital_id)
            except Exception:
                bot.send_message(message.chat.id, 'Больницы с таким адресом не существует!')

        request = f"""INSERT INTO doctor 
                    (first_name, middle_name, last_name, country, email, phone, birthdate, position, hospital_id)
                    VALUES ('{first_name}', '{middle_name}', '{last_name}', '{country}', '{email}', '{phone}', '{birthdate}', '{position}', '{hospital_id}');"""

        try:
            cursor.execute(request)
        except UniqueViolation:
            bot.send_message(message.chat.id, "Пользователь с таким Email/номером телефона уже существует!")
        except ForeignKeyViolation:
            bot.send_message(message.chat.id, "Больницы с такими данными не существует")
        else:
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, 'Врач успешно добавлен в базу данных!')


def add_patient(message):
    try:
        first_name, middle_name, last_name, address, email, phone, birthdate, doctor,  hospital_id, hospital_room_id = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Неверный формат сообщения!')
    else:
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOST,
            port=config.PORT
        )
        cursor = connection.cursor()
    if hospital_room_id.strip() == '-':
        request = f"""INSERT INTO patient
                            (first_name, middle_name, last_name, address, email, phone, birthdate, doctor, hospital_room_id, hospital_id )
                            VALUES ('{first_name}', '{middle_name}', '{last_name}', '{address}', '{email}', '{phone}', '{birthdate}', '{doctor}', '{hospital_room_id}', '{hospital_id}');"""


bot.infinity_polling()
