from __future__ import annotations

import datetime
import re

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.crud_country import country_crud
from app.crud.crud_ferry import ferry_crud
from app.crud.crud_port import port_crud
from app.db.session import get_or_create_session
from app.models import Country, Ferry, Port
from app.schemas.enums import Countries, CountriesAbbreviatedName
from app.telegtam_bot.keyboard import (
    generate_common_keyboard,
    generate_date_keyboard,
    generate_port_keyboard,
)

bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    from_pl_to_se = KeyboardButton("From PL to SE")
    from_se_to_pl = KeyboardButton("From SE to PL")
    main_menu = KeyboardButton("/start")

    keyboard.add(from_pl_to_se, from_se_to_pl, main_menu)
    await message.answer(f"Hi {message.from_user.first_name} -  {'Choose a direction.'}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["From PL to SE", "From SE to PL"])
async def handle_direction_selection(message: types.Message):
    is_pl_to_se = message.text == "From PL to SE"

    session = get_or_create_session()

    if f"{CountriesAbbreviatedName.PL.name} to SE" in message.text:
        country_departure = await country_crud.get_by_name(Countries.POLAND.value, session)
    else:
        country_departure = await country_crud.get_by_name(Countries.SWEDEN.value, session)

    keyboard = await generate_port_keyboard(country_departure, session)
    await session.close()

    country = "SE"
    if is_pl_to_se:
        country = "PL"
    await message.answer(f"Choose a port {country} of departure", reply_markup=keyboard)


@dp.message_handler(lambda message: re.match(r"^From .* to (SE|PL)$", message.text))
async def handle_port_selection(message: types.Message):
    # Get port name
    match = re.match(r"^From (.*) to (SE|PL)$", message.text)
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(2)

        keyboard = generate_common_keyboard(selected_port, selected_country)

        await message.answer("Please choose date", reply_markup=keyboard)
    else:
        # Handle cases where the message format doesn't match
        await message.answer("Invalid port selection format. Please choose a port.")


@dp.message_handler(lambda message: re.match(r"^Today from .* to (SE|PL)$", message.text))
async def handle_today_ferries(message: types.Message):
    match = re.match(r"^Today from (.*) to (SE|PL)$", message.text)
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(2)

        session = get_or_create_session()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        now = datetime.datetime.now()

        port_from = await port_crud.get_port_by_name(selected_port.lower(), session)
        country_to = await country_crud.get_by_name(
            CountriesAbbreviatedName.SE.value
            if selected_country == CountriesAbbreviatedName.SE.name
            else CountriesAbbreviatedName.PL.value,
            session,
        )

        ferries = await _get_ferries(port_from, country_to, now, session)
        formatted_ferries = await _format_ferries_as_string(ferries)

        await session.close()
        main_menu = KeyboardButton("/start")
        keyboard.add(main_menu)

        await message.answer(f"{formatted_ferries}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["Choose a date from PL to SE", "Choose a date from SE to PL"])
async def handle_choose_date(message: types.Message):
    direction = "PL to SE" if "PL to SE" in message.text else "SE to PL"

    keyboard = generate_date_keyboard()
    await message.answer(f"Please choose a date {direction}:", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("select_date:"))
async def handle_selected_date(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split(":")
    selected_date_str = data_parts[1]
    direction = data_parts[2]  # Extract the direction from callback data
    selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    user_id = callback_query.from_user.id

    # Now you can use the 'direction' variable to determine the selected direction
    # Perform actions accordingly based on the direction

    await callback_query.message.edit_text(f"You selected the date: {selected_date}, Direction: {direction}")


async def _get_ferries(port_from: Port, country_to: Country, date: datetime.date, session: AsyncSession) -> list[Ferry]:
    ports_to = await port_crud.get_ports_by_country_id(country_to.id, session)
    ferries = set()
    for port_to in ports_to:
        ferry = await ferry_crud.get_ferries(
            session, date=date, port_departure_id=port_from.id, port_arrival_id=port_to.id
        )
        if ferry:
            for one_ferry in ferry:
                ferries.add(one_ferry)

    return list(ferries)


async def _format_ferries_as_string(ferries):
    formatted_ferries = []

    for ferry_info in ferries:
        formatted_ferry = (
            f"Ferry name: {ferry_info.name}\n"
            f"Date: {ferry_info.date}\n"
            f"Departure Time: {ferry_info.time_departure}\n"
            f"Arrival Time: {ferry_info.time_arrival}\n"
        )
        formatted_ferries.append(formatted_ferry)

    return "\n".join(formatted_ferries)


# If you want start process polling without hooks
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
