import uuid
import random
import logging
import typing
import time

from aiogram import Bot, types, Dispatcher, executor, md
from aiogram.types import ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled
from aiogram.utils.helper import Helper, HelperMode

from main import *

class States(StatesGroup):
    mode = HelperMode.snake_case
    AUTH_0 = State()
    AUTH = State()
    packagename_input = State()
    apkname_input = State()

class StatesAddTokenToBd(StatesGroup):
    send_token_text = State()


bot = Bot(token='2073805665:AAFOmin2MoyFag_LtFDIvvTpfTB49g1NPto')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

inline_kb_full = InlineKeyboardMarkup()
inline_kb_full.add(InlineKeyboardButton('1. ДОБАВИТЬ SSH КЛЮЧЬ НА АКК', callback_data='addtokentodb')).add(InlineKeyboardButton('2. УБРАТЬ СЕРВЕРА', callback_data='dproxy')).add(InlineKeyboardButton('3. СОЗДАТЬ СЕРВЕРА', callback_data='cservers')).add(InlineKeyboardButton('4. СОЗДАТЬ ПРОКСИ НА СЕРВЕРАХ', callback_data='cproxy'))
inline_kb_back = InlineKeyboardMarkup().add(InlineKeyboardButton('назад', callback_data='back'))
menu_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('ДОБАВИТЬ ТОКЕНs В БД', callback_data='addtobd'), InlineKeyboardButton('ПОДНЯТИЕ', callback_data='standup'), InlineKeyboardButton('ДОБАВИТЬ SSH КЛЮЧЬ НА АКК', callback_data='addtokentodb'))

## start command
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state=FSMContext):

    await message.reply('ОЖИДАЮ ТОКЕН \n\nДЛЯ НЕСКОЛЬКИХ ТОКЕНОВ: СКИДОВАТЬ В ФОРМАТЕ \n\ntoken1\ntoken2\ntoken3\ntoken4')

    await States.AUTH_0.set()

## add token to bd path ##########################################################################################################
@dp.callback_query_handler(text='addtobd', state=States.AUTH_0)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext, message = types.Message):

    await message.reply(f'ВЫБОР ДЕЙСТВИЙ, НАПОМИНАЮ ЧТО ВЫБРАННЫЕ АККАКНТЫ ЭТО: \n{ocean_token}', reply_markup=inline_kb_full)
    await States.AUTH.set()

## upping of servers #############################################################################################################
@dp.message_handler(state=States.AUTH_0)
async def get_auth_passwords(message: types.Message, state=FSMContext):
    ocean_token = message.text.split('\n')

    try: ocean_token = check_id_tokens_valid(ocean_token)[0]
    except Exception as e: print(e)

    async with state.proxy() as data:
        data['ocean_tokens'] = ocean_token

    if len(ocean_token) == 0:
        await message.reply(f'У ВАС НЕТ ВАЛИДНЫХ ТОКЕНОВ, ПОЖАЛУЙСТА ПОВТОРНО ВВЕДИТЕ ТОКЕНЫ')

    else:
        print(message.from_user.id)
        await message.reply(f'ВЫБОР ДЕЙСТВИЙ, НАПОМИНАЮ ЧТО ВЫБРАННЫЕ АККАКНТЫ ЭТО: \n{ocean_token}', reply_markup=inline_kb_full)
        await States.AUTH.set()


@dp.callback_query_handler(text='back', state=States.AUTH_0)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext, message = types.Message):
    ocean_token = message.text.split('\n')

    async with state.proxy() as data:
        ocean_token = data['ocean_tokens']

    await message.reply(f'ВЫБОР ДЕЙСТВИЙ, НАПОМИНАЮ ЧТО ВЫБРАННЫЕ АККАКНТЫ ЭТО: \n{ocean_token}', reply_markup=inline_kb_full)
    await States.AUTH.set()

## DELETE
@dp.callback_query_handler(text='dproxy', state=States.AUTH)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'УДАЛЯЮ ПРОКСИ НА СЕРВЕРАХ')

    async with state.proxy() as data:
            oc_token = data['ocean_tokens']

    for i in oc_token:
        try: delete_proxies(i)
        except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    await bot.send_message(callback_query.from_user.id, 'ПРОКСИ БЫЛИ УДАЛЕНЫ. СКИНЬТЕ ТОКЕНЫ ПОВТОРНО')
    await States.AUTH_0.set()

countries_cb = CallbackData('post', 'id', 'country')  # post:<id>:<action>
markup = types.InlineKeyboardMarkup()
post_id = 000
markup.add(types.InlineKeyboardButton('USA', callback_data=countries_cb.new(id=post_id, country='usa')))
markup.add(types.InlineKeyboardButton('GB', callback_data=countries_cb.new(id=post_id, country='gb')))
markup.add(types.InlineKeyboardButton('CA', callback_data=countries_cb.new(id=post_id, country='ca')))
markup.add(types.InlineKeyboardButton('DE', callback_data=countries_cb.new(id=post_id, country='de')))


## CREATE SERVERS 1
@dp.callback_query_handler(text='cservers', state=States.AUTH)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'выберете страну', reply_markup=markup)

## CREATE SERVERS 2
@dp.callback_query_handler(countries_cb.filter(country=['usa', 'gb', 'ca', 'de']), state=States.AUTH)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext, callback_data: typing.Dict[str, str]):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'запущенно создание servers. примерно 2 минуты ')

    country = callback_data['country']

    async with state.proxy() as data:
        oc_token = data['ocean_tokens']

    if country == 'usa':
        for i in oc_token:
            try: create_servers(i, 'nyc1')
            except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    if country == 'gb':
        for i in oc_token:
            try: create_servers(i, 'lon1')
            except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    if country == 'ca':
        for i in oc_token:
            try: create_servers(i, 'tor1')
            except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    if country == 'de':
        for i in oc_token:
            try: create_servers(i, 'fra1')
            except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    time.sleep(70)

    await bot.send_message(callback_query.from_user.id, 'сервера были созданны, скинте токен повторно')
    await States.AUTH_0.set()

## ADD TOKEN TO DB OF BOT
@dp.callback_query_handler(text='addtokentodb', state=States.AUTH)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'запущенно добавление ssh в каб')

    async with state.proxy() as data:
        oc_token = data['ocean_tokens']

    for i in oc_token:
        try: add_openssh_to_account(i); await bot.send_message(callback_query.from_user.id, f'{i} \n\nбыл добавлен ssh ключь')
        except Exception as e: await bot.send_message(callback_query.from_user.id, f'{i} \n\nвыдал ошибку: \n\n{e}')

    await bot.send_message(callback_query.from_user.id, 'ssh были добавлены в кабы. и записанны в бд')
    await States.AUTH_0.set()

## CREATE PROXIES
@dp.callback_query_handler(text='cproxy', state=States.AUTH)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'запущенно создание proxy')

    async with state.proxy() as data:
        oc_token = data['ocean_tokens']
    print(oc_token)
    try: multi_setup_servers(oc_token)
    except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    await bot.send_message(callback_query.from_user.id, 'НА СЕРВЕРАХ БЫЛО РАЗВЁРНУТО ОКРУЖЕНИЕ')

    try: list_of_server_ips = multi_proxy_start(oc_token)
    except Exception as e: await bot.send_message(callback_query.from_user.id, f'была поймана ошибка {e}')

    proxy_string = ''

    for i in list_of_server_ips:
        proxy_string = proxy_string + f"{i.split(':')[0]}:3128\n"

    await bot.send_message(callback_query.from_user.id, proxy_string)
    await States.AUTH_0.set()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    create_bdx()
    executor.start_polling(dp, on_shutdown=shutdown)
