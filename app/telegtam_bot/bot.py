import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from app.crud.crud_ferry import ferry_crud
from app.crud.crud_country import country_crud
from app.crud.crud_port import port_crud
from app.core.config import settings
from app.db.session import get_or_create_session
from app.schemas.enums import Countries

bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    from_pl_to_se = KeyboardButton("From PL to SE")
    from_se_to_pl = KeyboardButton("From SE to PL")

    keyboard.add(from_pl_to_se, from_se_to_pl)
    await message.answer(f"{message.from_user.first_name} -  {'Choose a direction.'}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "From PL to SE")
async def handle_pl_to_se(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    today = KeyboardButton("Today from PL to SE")
    coose_date = KeyboardButton("Choose a date")
    main_menu = KeyboardButton("/start")

    keyboard.add(today, coose_date, main_menu)
    await message.answer("PL to SE", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "From SE to PL")
async def handle_se_from_pl(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    today = KeyboardButton("Today from SE to PL")
    coose_date = KeyboardButton("Choose a date")
    main_menu = KeyboardButton("/start")

    keyboard.add(today, coose_date, main_menu)
    await message.answer("SE to PL", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Today from PL to SE")
async def handle_today_pl_se(message: types.Message):
    session = get_or_create_session()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    now = datetime.datetime.now()
    country_from = await country_crud.get_by_name(Countries.POLAND.value, session)
    country_to = await country_crud.get_by_name(Countries.SWEDEN.value, session)
    ferries = await _get_ferries(country_from, country_to, now, session)

    await session.close()
    main_menu = KeyboardButton("/start")
    keyboard.add(main_menu)

    await message.answer(f"{list(ferries)[:10]}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Today from SE to PL")
async def handle_today_se_pl(message: types.Message):
    session = get_or_create_session()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    now = datetime.datetime.now()
    country_from = await country_crud.get_by_name(Countries.SWEDEN.value, session)
    country_to = await country_crud.get_by_name(Countries.POLAND.value, session)
    ferries = await _get_ferries(country_from, country_to, now, session)

    await session.close()
    main_menu = KeyboardButton("/start")
    keyboard.add(main_menu)

    await message.answer(f"{list(ferries)[:10]}", reply_markup=keyboard)


async def _get_ferries(country_from, country_to, date, session):
    ports_from = await port_crud.get_ports_by_country_id(country_from.id, session)
    ports_to = await port_crud.get_ports_by_country_id(country_to.id, session)
    ferries = set()
    for port_from in ports_from:
        for port_to in ports_to:
            ferry = await ferry_crud.get_ferries(session, date=date, port_departure_id=port_from.id,
                                                 port_arrival_id=port_to.id)
            if ferry:
                for one_ferry in ferry:
                    ferries.add(one_ferry)
    return ferries

# If you want start process polling without hooks
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
