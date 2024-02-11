from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from datetime import datetime
import asyncio
import pymysql
import time
import os
import binascii
import cv2

bot = Bot('6927406876:AAGJcJM2NQ2dVCtK83AEWYjElFqP2qN6hAQ')
dp = Dispatcher(bot, storage=MemoryStorage())

img, data, tm, lat, lon, role = 0, 0, 0, 0, 0, 0

try:
    connection = pymysql.connect(
        host="localhost",
        port=3306,
        user="t_bot",
        password="tebot3487!#",
        database="shoreline",
    )
except Exception as ex:
    print("ошибка:", ex)


class Form(StatesGroup):
    i_data = State()
    i_time = State()
    i_geo = State()
    c_geo = State()
    check = State()
    no_check = State()
    m_stg = State()


def calc(fl):
    image = cv2.imread(fl)
    resized = cv2.resize(image, (8, 8), interpolation=cv2.INTER_AREA)
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    avg = gray_image.mean()
    ret, threshold_image = cv2.threshold(gray_image, avg, 255, 0)
    _hash = ""
    for x in range(8):
        for y in range(8):
            val = threshold_image[x, y]
            if val == 255:
                _hash = _hash + "1"
            else:
                _hash = _hash + "0"
    return _hash


def compare(h1, h2):
    e = len(h1)
    j = 0
    count = 0
    while j < e:
        if h1[j] != h2[j]:
            count = count + 1
        j = j + 1
    return count


HC = ''

kb = ReplyKeyboardMarkup
kb.add(KeyboardButton(text='/start'))


@dp.message_handler(commands=['start'])
async def welcoming(message: types.Message, state: FSMContext):
    await state.reset_state()
    global role
    with connection.cursor() as cursor:
        user_id = message.from_user.id
        cursor.execute("SELECT id_u FROM users WHERE id_u='" + str(user_id) + "'")
        rows = cursor.fetchall()
        if rows == ():
            insert_query = "INSERT INTO users (id_u, role, rep) VALUES ('" + str(user_id) + "', 0, 0);"
            cursor.execute(insert_query)
            role = 0
            connection.commit()
        else:
            cursor.execute("SELECT role FROM users WHERE id_u='" + str(user_id) + "'")
            rows = cursor.fetchall()
            role = rows[0][0]

    if role > -1:
        await state.set_state(Form.check)
    else:
        await state.set_state(Form.no_check)

    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardMarkup(text='отправить фото', callback_data='foto')
    #ib2 = InlineKeyboardMarkup(text='модерация', callback_data='moder')
    ikb.add(ib1) # если когда-то продолжим добавить , ib2
    await message.answer(text='выберете опцию', reply_markup=ikb)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HC)

'''     Модератор   '''

@dp.callback_query_handler(text='moder', state=Form.no_check)
async def nemoder(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('вы не можете это сделать, вы забанены')
    await state.reset_state()

@dp.callback_query_handler(text='moder', state=Form.check)
async def moderator(callback: types.CallbackQuery, state: FSMContext):
    global role
    if role != 1:
        await callback.message.answer('вы не можете это сделать, вы не являетесь администратором')
        await state.reset_state()
    else:
        ikb = InlineKeyboardMarkup(row_width=2)
        ib1 = InlineKeyboardMarkup(text='подозрительные изображения', callback_data='strange')
        ib2 = InlineKeyboardMarkup(text='забаненные изображения', callback_data='banned')
        ikb.add(ib1, ib2)
        await callback.message.answer('вам доступны функции модератора, чем займётесь?\nПодозрительные. Проверяйте'
                                      ' изображения, на которые жалуются и решайте их судьбу', reply_markup=ikb)

    @dp.callback_query_handler(text='strange', state=Form.check)
    async def stg_i(callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.message.from_user.id
        with connection.cursor() as cursor:
            cursor.execute("SELECT count, reason, id_i FROM moderation WHERE NOT EXISTS (SELECT 1 FROM banned WHERE "
                           "banned.id_i = moderation.id_i);")
            rows = cursor.fetchall()
            c = max(map(lambda t: t, rows))
            c = str(c[2])
            cursor.execute("SELECT picture FROM images WHERE images.id_i = " + c + ";")
            rows = cursor.fetchall()

        if os.name == 'nt':
            sp = r'\ '[0]
        else:
            sp = '/'

        with open('tmp' + sp + 'deimg' + str(user_id) + '.png', 'wb') as fle:
            fle.write(binascii.unhexlify(rows[0][0]))

        await bot.send_photo(chat_id=callback.message.chat.id, photo='tmp' + sp + 'deimg' + str(user_id) + '.png')
        await state.set_state(Form.m_stg)

'''     Обычный user    '''

@dp.callback_query_handler(text='foto', state=Form.no_check)
async def take_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('вы не можете отправлять фото, вы забанены')
    await state.reset_state()


@dp.callback_query_handler(text='foto', state=Form.check)
async def photo(callback: types.CallbackQuery):
    await callback.message.answer('пришлите фото')

    @dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.check)
    async def take_photo(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        global img
        img = message.photo[-1]
        if os.name == 'nt':
            sp = r'\ '[0]
        else:
            sp = '/'
        await img.download(destination_file='tmp' + sp + 'img' + str(user_id) + '.png')
        with open('tmp' + sp + 'img' + str(user_id) + '.png', 'rb') as fle:
            img = binascii.hexlify(fle.read())

        s = 0
        fl = 'tmp' + sp + 'img' + str(user_id) + '.png'
        flc = len(os.listdir('img_base'))
        hs1 = calc(fl)

        for i in range(flc):
            hs2 = calc(r'img_base\c' + str(i) + '.png')
            sm = compare(hs1, hs2)
            if sm < 20:
                s += 1

        if s <= round(flc/50, 0):
            await message.answer('Мы не можем добавить это фото\nОно слишком странное')
        elif s <= round(flc/5, 0):
            ikb = InlineKeyboardMarkup(row_width=2)
            ib1 = InlineKeyboardMarkup(text='да', callback_data='ok')
            ib2 = InlineKeyboardMarkup(text='нет, снова', callback_data='_')
            ikb.add(ib1, ib2)
            await message.answer('Вы уверены, что добавляете правильное фото?', reply_markup=ikb)

            @dp.callback_query_handler(text='ok', state=Form.check)
            async def checking(callback: types.CallbackQuery, state: FSMContext):
                ikb = InlineKeyboardMarkup(row_width=1)
                ib1 = InlineKeyboardMarkup(text='скинуть гео', callback_data='geo')
                ib2 = InlineKeyboardMarkup(text='я с компьютера', callback_data='comp')
                ikb.add(ib1, ib2)
                await message.answer('Где это место?', reply_markup=ikb)

            @dp.callback_query_handler(text='comp', state=Form.check)
            async def geo_c(callback: types.CallbackQuery, state: FSMContext):
                await message.answer(
                    'Укажите широту, через пробел долготу\nМожете влючить карты и найти геопозицию там')
                await state.set_state(Form.c_geo)

            @dp.callback_query_handler(text='geo', state=Form.check)
            async def geo_i(callback: types.CallbackQuery, state: FSMContext):
                await message.answer('скрепка > геопозиция > отправить выбранную')
                await state.set_state(Form.i_geo)
        else:
            ikb = InlineKeyboardMarkup(row_width=1)
            ib1 = InlineKeyboardMarkup(text='скинуть гео', callback_data='geo')
            ib2 = InlineKeyboardMarkup(text='я с компьютера', callback_data='comp')
            ikb.add(ib1, ib2)
            await message.answer('Где это место?', reply_markup=ikb)

        @dp.callback_query_handler(text='comp', state=Form.check)
        async def geo_c(callback: types.CallbackQuery, state: FSMContext):
            await message.answer('Укажите широту, через пробел долготу\nМожете влючить карты и найти геопозицию там')
            await state.set_state(Form.c_geo)

        @dp.callback_query_handler(text='geo', state=Form.check)
        async def geo_i(callback: types.CallbackQuery, state: FSMContext):
            await message.answer('скрепка > геопозиция > отправить выбранную')
            await state.set_state(Form.i_geo)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=Form.i_geo)
async def take_geo_i(message: types.Message, state: FSMContext):
    global lat, lon
    loc = message.location
    lat = loc.latitude
    lon = loc.longitude
    if (45.006 < float(lat) < 47.71) and (33.55 < float(lon) < 39.82):
        await message.answer('Принято, когда было сделано это фото?\nукажите дату в формате ДД-ММ-ГГГГ')
        await state.set_state(Form.i_data)
    else:
        await message.answer(
            'Бот работает только с побережьями азовского моря, а это за его пределами\nПопробуйте ещё раз')


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.c_geo)
async def take_geo_c(message: types.Message, state: FSMContext):
    global lat, lon
    loc = message.text.split()
    try:
        lat = loc[0]
        lon = loc[1]
        if (45.006 < float(lat) < 47.71) and (33.55 < float(lon) < 39.82):
            await message.answer('Принято, когда было сделано это фото?\nукажите дату в формате ДД-ММ-ГГГГ')
            await state.set_state(Form.i_data)
        else:
            await message.answer(
                'Бот работает только с побережьями азовского моря, а это за его пределами\nПопробуйте ещё раз')
    except:
        await message.answer('Вы неверно ввели координаты, попробуйте ещё раз')


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.i_data)
async def take_data(message: types.Message, state: FSMContext):
    try:
        global data
        data = message.text
        data = data[6:] + '-' + data[3:5] + '-' + data[:2]
        time.strptime(data, '%Y-%m-%d')
        if 1826 <= int(data[0:4]) <= int(str(datetime.now())[0:4]):
            await message.answer('Отлично, помните ли время когда его сделали?\nВремя в формате ЧЧ:ММ:СС, можно указать'
                                 ' только час или час и минуты\nЕсли не помните, то в ответ отправьте -'
                                 '\nЧтобы отправить текущее время отправьте @')
            await state.set_state(Form.i_time)
        elif int(str(datetime.now())[0:4]) < int(data[0:4]):
            await message.answer('Мне кажется вы не могли сделать фото в ' + data[0:4] + ' году, когда на дворе только '
                                 '' + str(datetime.now())[0:4] + '\nПопробуйте ввести ещё раз')
        else:
            await message.answer('По данным с интернета первые фото появились в 1826, вы явно не могли сфоткать '
                                 'ничего раньше этого года\nПопробуйте ввести ещё раз')
    except ValueError:
        await message.answer("Вы некорректно ввели дату, попробуйте ввести ещё раз")


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.i_time)
async def take_time(message: types.Message, state: FSMContext):
    try:
        global img, data, tm, lon, lat
        tm = message.text
        if tm == "@":
            tm = str(datetime.now())[11:19]
        elif tm != '-':
            if len(tm) < 8:
                tm += '0' * (8 - len(tm))
            tm = tm[:2] + ':' + tm[3:5] + ':' + tm[6:]
            time.strptime(tm, '%H:%M:%S')

        try:
            with connection.cursor() as cursor:
                lon = round(float(lon), 3)
                lat = round(float(lat), 3)
                if tm != '-':
                    insert_query = ("INSERT INTO images (picture, date_i, time_i, lon, lat, id_u) "
                                    "VALUES ('" + str(img)[2:-1] + "', '" + str(data) + "', '" + str(tm) + "', "
                                    "" + str(lon) + ", " + str(lat) + ", " + str(message.from_user.id) + ");")
                else:
                    insert_query = ("INSERT INTO images (picture, date_i, lon, lat, id_u) "
                                    "VALUES ('" + str(img)[2:-1] + "', '" + str(data) + "', "
                                    "" + str(lon) + ", " + str(lat) + ", " + str(message.from_user.id) + ");")
                cursor.execute(insert_query)
                connection.commit()

                user_id = message.from_user.id
                if os.name == 'nt':
                    sp = r'\ '[0]
                else:
                    sp = '/'

                os.remove('tmp' + sp + 'img' + str(user_id) + '.png')

        except Exception as ex:
            print(ex)

        await message.answer('Спасибо за содействие!')
        await state.reset_state()
    except ValueError:
        await message.answer("Вы некорректно ввели время, попробуйте ввести ещё раз")


if __name__ == '__main__':
    executor.start_polling(dp)
