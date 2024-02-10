import asyncio
import numpy as np
import pymysql
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from datetime import datetime
import time

bot = Bot('6927406876:AAGJcJM2NQ2dVCtK83AEWYjElFqP2qN6hAQ')
dp = Dispatcher(bot, storage=MemoryStorage())

img, data, tm, lat, lon = 0, 0, 0, 0, 0

# try:
#     connection = pymysql.connect(
#         host="localhost",
#         port=3306,
#         user="t_bot",
#         password="tebot3487!#",
#         database="shoreline",
#     )
# except Exception as ex:
#     print("ошибка:", ex)


class Form(StatesGroup):
    i_data = State()
    i_time = State()
    i_geo = State()
    c_geo = State()


HC = 'ДАУН!'

kb = ReplyKeyboardMarkup
kb.add(KeyboardButton(text='/start'))


@dp.message_handler(commands=['start'])
async def welcoming(messege: types.Message, state: FSMContext):
    await state.reset_state()
    ikb = InlineKeyboardMarkup(row_width=2)
    ib1 = InlineKeyboardMarkup(text='отправить фото', callback_data='foto')
    ikb.add(ib1)
    await messege.answer(text='выберете опцию', reply_markup=ikb)


@dp.message_handler(commands=['help'])
async def help_command(messege: types.Message):
    await messege.answer(text=HC)


@dp.callback_query_handler(text='foto')
async def photo(callback: types.CallbackQuery):
    await callback.message.edit_text('пришлите фото')

    @dp.message_handler(content_types=types.ContentType.PHOTO)
    async def take_photo(message: types.Message, state: FSMContext):

        # with connection.cursor() as cursor:
        #     user_id = message.from_user.id
        #     cursor.execute("SELECT id_u FROM users WHERE id_u='"+str(user_id)+"'")
        #     rows = cursor.fetchall()
        #     if rows == ():
        #         insert_query = "INSERT INTO users (id_u, role, rep) VALUES ('" + str(user_id) + "', 0, 0);"
        #         cursor.execute(insert_query)
        #         # connection.commit()           # раскоментить в финальной версии (сохранение данных в бд)

            global img
            img = message.photo[-1].file_id
            print(img)

            ikb = InlineKeyboardMarkup(row_width=1)
            ib1 = InlineKeyboardMarkup(text='скинуть гео', callback_data='geo')
            ib2 = InlineKeyboardMarkup(text='я с компьютера', callback_data='comp')
            ikb.add(ib1, ib2)
            await message.answer('Где это место?', reply_markup=ikb)

            @dp.callback_query_handler(text='comp')
            async def geo_c(callback: types.CallbackQuery, state: FSMContext):
                await message.answer('Укажите широту, через пробел долготу\nМожете влючить карты и найти геопозицию там')
                await state.set_state(Form.c_geo)

            @dp.callback_query_handler(text='geo')
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
            await message.answer('Бот работает только с побережьями азовского моря, а это за его пределами\nПопробуйте ещё раз')
    except:
        await message.answer('Вы неверно ввели координаты, попробуйте ещё раз')


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.i_data)
async def take_data(message: types.Message, state: FSMContext):
    try:
        global data
        data = message.text
        data = data[6:]+'-'+data[3:5]+'-'+data[:2]
        time.strptime(data, '%Y-%m-%d')
        if 1826 <= int(data[0:4]) <= int(str(datetime.now())[0:4]):
            await message.answer('Отлично, помните ли время когда его сделали?\nВремя в формате ЧЧ:ММ:СС, можно указать'
                                 ' только час или час и минуты\nЕсли не помните, то в ответ отправьте -')
            await state.set_state(Form.i_time)
        elif int(str(datetime.now())[0:4]) < int(data[0:4]):
            await message.answer('Мне кажется вы не могли сделать фото в '+data[0:4]+' году, когда на дворе только '
                                 ''+str(datetime.now())[0:4]+'\nПопробуйте ввести ещё раз')
        else:
            await message.answer('По данным с интернета первые фото появились в 1826, вы явно не могли сфоткать '
                                 'ничего раньше этого года\nПопробуйте ввести ещё раз')
    except ValueError:
        await message.answer("Вы некорректно ввели дату, попробуйте ввести ещё раз")


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.i_time)
async def take_time(message: types.Message, state: FSMContext):
    try:
        global tm
        tm = message.text
        if tm != '-':
            if len(tm) < 8:
                tm += '0' * (8 - len(tm))
            tm = tm[:2]+':'+tm[3:5]+':'+tm[6:]
            time.strptime(tm, '%H:%M:%S')

#         try:
#             with connection.cursor() as cursor:
#                 if tm != '-':
#                     insert_query = ("INSERT INTO images (picture, date_i, time_i, lon, lat, id_u) "
#                                     "VALUES ("+str(img)+", '" + str(data) + "', '" + str(tm) + "', " + str(lon) + ", "
#                                     "" + str(lat) + ", " + str(message.from_user.id) + ");")
#                 else:
#                     insert_query = ("INSERT INTO images (picture, date_i, lon, lat, id_u) "
#                                     "VALUES (" + str(img) + ", '" + str(data) + "', '" + str(lon) + "', "
#                                     "" + str(lat) + ", " + str(message.from_user.id) + ");")
#                 cursor.execute(insert_query)
#                 # connection.commit()           # раскоментить в финальной версии (сохранение данных в бд)
#         except Exception as ex:
#             print(ex)
#
        await message.answer('Спасибо за содействие!')
        await state.reset_state()
    except ValueError:
        await message.answer("Вы некорректно ввели время, попробуйте ввести ещё раз")


if __name__ == '__main__':
    executor.start_polling(dp)
