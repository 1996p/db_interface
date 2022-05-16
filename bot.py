import telebot
import config
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from datetime import date
from PIL import Image, ImageFont, ImageDraw

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
    send = bot.send_message(message.chat.id,'Какую информацию Вы хотите получить? \n1) Больницу(общая информация) \n2) О враче(пациенте, контакты, место работы)\n3) О лаборатории(не ебу че это за залупа ваще, хз че с ней делать)\n4) О пациенте(лежит ли стационаре, в какой палате, диагноз, результаты анализов, лечущий врач, номер больницы)\n  5) О палате(персонал, больные)')
    bot.register_next_step_handler(send, get_category)


def get_category(message):

    match message.text:

        case '1':
            answer_text = 'Введите адрес или номер больницы, о которой Вы хотите получить информацию'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, get_hospital)

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


def get_hospital(message):
    connection = psycopg2.connect(
        database=config.DATABASE,
        user=config.USER,
        password=config.PASSWORD,
        host=config.HOST,
        port=config.PORT
    )
    cursor = connection.cursor()
    if len(message.text) >= 4:
        request = f"SELECT * FROM hospital WHERE address = '{message.text}';"
    else:
        request = f"SELECT * FROM hospital WHERE id = {message.text}"

    cursor.execute(request)

    hospital_number, hospital_address = cursor.fetchall()[0]

    image = Image.open('hospital_card.jpeg')
    font = ImageFont.truetype('C:\\Users\\dursi\\PycharmProjects\\pythonProject2\\a_MachinaOrtoSls_Bold.ttf', size=37)
    draw = ImageDraw.Draw(image)
    formatted_address = list(hospital_address)
    print('1', formatted_address)
    draw.text((415, 343),
              f'Больница №{hospital_number}',
              fill=('#1C0606'),
              font=font)
    draw.text(
        (415, 385),
        f'адрес: {"".join(formatted_address[:hospital_address.find("ул.")-1])}',
        fill=('#1C0606'),
        font=font
    )
    draw.text(
        (414, 428),
        f'{"".join(formatted_address[hospital_address.find("ул."):])}',
        fill=('#1C0606'),
        font=font
    )
    bot.send_photo(message.chat.id, image)


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

    match message.text.strip():
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
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_patient)
        case '6':
            answer_text = 'Чтобы добавить анализы, необходимо написать их в следующем формате:\n*фамилия и инициалы пациента*, *результаты анализов крови*, *результаты анализов мочи*, *результаты анализов кала*'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_analysis)
        case '7':
            answer_text = 'Чтобы добавить пациента, необходимо написать их в следующем формате:\n*имя*; *отчество*; *фамилия*; *место проживания*; *электронная почта*; *номер телефона*;\n*дата рождения*; *номер палаты*; *номер больницы(адрес больницы)*'
            send = bot.send_message(message.chat.id, answer_text)
            bot.register_next_step_handler(send, add_staff)
        case '8':
            answer_text = 'Чтобы добавить диагноз пациента, необходимо написать данные в следующем формает:\n*фамилия и инициалы пациента*, *содержание диагноза*'
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
        print(message.text.split(';'))
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

        if len(hospital_id) > 3:
            cursor.execute(f"SELECT id FROM hospital WHERE address LIKE '%{hospital_id.strip()}%'")
            hospital_id = cursor.fetchall()[0][0]

        doctor_last_name, doctor_name = doctor.split()
        print(doctor.split())
        print(f"SELECT id, first_name, middle_name FROM doctor WHERE last_name  LIKE '%{doctor_last_name.strip()}%' AND hospital_id = {hospital_id.strip()}")
        cursor.execute(f"SELECT id, first_name, middle_name FROM doctor WHERE last_name  LIKE '%{doctor_last_name.strip()}%' AND hospital_id = '{hospital_id.strip()}'")
        doctor_id = None

        for doctor in cursor.fetchall():
            print(doctor)
            if doctor[1].strip().startswith(doctor_name[0]) and doctor[2].strip().startswith(doctor_name[2]):
                doctor_id = doctor[0]

        if doctor_id is None:
            bot.send_message(message.chat.id, 'Такого доктора больнице нет! ')
            return

        if hospital_room_id.strip() == '-':
            request = f"""INSERT INTO patient
                        (first_name, middle_name, last_name, address, email, phone, birthdate, doctor_id, hospital_id)
                        VALUES ('{first_name}', '{middle_name}', '{last_name}', '{address}', '{email}', '{phone}', '{birthdate}', '{doctor_id}', '{hospital_id}');"""
        else:
            request = f"""INSERT INTO patient
                        (first_name, middle_name, last_name, address, email, phone, birthdate, doctor_id, hospital_room_id, hospital_id)
                        VALUES ('{first_name}', '{middle_name}', '{last_name}', '{address}', '{email}', '{phone}', '{birthdate}', '{doctor_id}','{hospital_room_id}', '{hospital_id}');"""

        try:
            cursor.execute(request)
        except Exception as exc:
            print(exc)

        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, 'Новый пользователь успешно создан!')


def add_analysis(message):
    try:
        patient_data, blood_result, urine_result, cal_result = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Неверный формат сообщения')
        return

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
            patient_last_name, patient_name = patient_data.split()
        except Exception:
            bot.send_message(message.chat.id, "Имя пациента указано неверно!")
            return

        try:
            cursor.execute(f"SELECT id, first_name, middle_name FROM patient WHERE last_name LIKE '%{patient_last_name.strip()}%'")
        except Exception:
            bot.send_message(message.chat.id, 'Такого пациента нет!')
            return

        patient_id = None
        for patient in cursor.fetchall():
            if patient[1].strip().startswith(patient_name[0]) and patient[2].strip().startswith(patient_name[2]):
                patient_id = patient[0]

        if patient_id is not None:
            cursor.execute(f"INSERT INTO analys (blood_result, cal_result, urine_result, patient_id) VALUES ('{blood_result}', '{cal_result}', '{urine_result}', {patient_id});")
        else:
             bot.send_message(message.chat.id, 'Такого пациента нет!')

        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, 'Анализы успешно добавлены!')


def add_staff(message):
    try:
        print(message.text.split(';'))
        first_name, middle_name, last_name, address, email, phone, birthdate, hospital_room_id, hospital_id = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Неверный формат сообщения!')
    else:
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            port=config.PORT,
            host=config.HOST,
        )

        cursor = connection.cursor()

        if len(hospital_id) > 3:
            cursor.execute(f"SELECT id FROM hospital WHERE address LIKE '%{hospital_id.strip()}%'")
            hospital_id = cursor.fetchall()[0][0]

        request = f"""INSERT INTO staff
                     (first_name, middle_name, last_name, address, email, phone, birthdate, hospital_room_id, hospital_id)
                     VALUES ('{first_name}', '{middle_name}', '{last_name}', '{address}', '{email}', '{phone}', '{birthdate}','{hospital_room_id}', '{hospital_id}');"""

        try:
            cursor.execute(request)
        except Exception as exc:
            print(exc)
            bot.send_message(message.chat.id, 'Произошла ошибка при добавлении персонала!')
        else:
            connection.commit()
            connection.close()


def add_diagnosis(message):
    try:
        patient_data, diagnosis = message.text.split(';')
    except Exception:
        bot.send_message(message.chat.id, 'Неверный формат сообщения')
    else:
        connection = psycopg2.connect(
            database=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            port=config.PORT,
            host=config.HOST,
        )

        cursor = connection.cursor()

        patient_last_name, patient_name = patient_data.split(';')

        try:
            cursor.execute(f"SELECT id, first_name, last_name FROM patient WHERE last_name = '{patient_last_name}'" )
        except Exception:
            bot.send_message(message.chat.id, "Такого пациента нет!")
            return
        else:
            patient_id = None
            for patient in cursor.fetchall():
                if patient[1].strip().startswith(patient_name[0]) and patient[2].strip().startswith(patient_name[2]):
                   patient_id = patient[0]

            if patient_id is not None:
                try:
                    cursor.execute(f"INSERT INTO conclusion (patient_id, content, date) VALUES ({patient_id}, '{diagnosis}', '{date.today()}')")
                    connection.commit()
                except Exception:
                    bot.send_message(message.chat.id, 'Возникла ошибка при добавлении диагноза в базу данных')
                else:
                    connection.close()
                    bot.send_message(message.chat.id, 'Диагноз успешно создан')


bot.infinity_polling()
