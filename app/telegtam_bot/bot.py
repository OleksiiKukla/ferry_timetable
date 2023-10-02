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

    async with get_or_create_session() as session:

        if f"{CountriesAbbreviatedName.PL.name} to SE" in message.text:
            country_departure = await country_crud.get_by_name(Countries.POLAND.value, session)
        else:
            country_departure = await country_crud.get_by_name(Countries.SWEDEN.value, session)

        keyboard = await generate_port_keyboard(country_departure, session)

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

        async with get_or_create_session() as session:
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

        main_menu = KeyboardButton("/start")
        keyboard.add(main_menu)

        await message.answer(f"{formatted_ferries}", reply_markup=keyboard)


@dp.message_handler(lambda message: re.match(r"^Choose a date from .* to (SE|PL)$", message.text))
async def handle_choose_date(message: types.Message):
    match = re.match(r"^Choose a date from (.*) to (SE|PL)$", message.text)
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(2)

    keyboard = generate_date_keyboard(selected_port, selected_country)
    await message.answer(
        f"Please choose a departure date from {selected_port.capitalize()} to {selected_country}:",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("Selected date from"))
async def handle_selected_date(callback_query: types.CallbackQuery):
    match = re.match(r"^Selected date from (.*) to (SE|PL): (.*)$", callback_query.data)
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(2)
        selected_date = match.group(3).strip()

    selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d")

    async with get_or_create_session() as session:
        port_from = await port_crud.get_port_by_name(selected_port.lower(), session)
        country_to = await country_crud.get_by_name(
            CountriesAbbreviatedName.SE.value
            if selected_country == CountriesAbbreviatedName.SE.name
            else CountriesAbbreviatedName.PL.value,
            session,
        )
        ferries = await _get_ferries(port_from, country_to, selected_date, session)
        formatted_ferries = await _format_ferries_as_string(ferries)

    user_id = callback_query.from_user.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = KeyboardButton("/start")
    keyboard.add(main_menu)

    await callback_query.message.answer(f"{formatted_ferries}", reply_markup=keyboard)


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


async def _format_ferries_as_string(ferries: list[Ferry]):
    formatted_ferries = []
    ferries = sorted(ferries, key=lambda ferry: ferry.time_departure)

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
