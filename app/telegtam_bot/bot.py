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
from app.crud.crud_user import user_crud
from app.db.session import get_or_create_session
from app.models import Country, Ferry, Port, User
from app.schemas.enums import Countries, CountriesAbbreviatedName, Languages
from app.schemas.user_schemas import UserCreateSchemas
from app.telegtam_bot.keyboard import (
    generate_common_keyboard,
    generate_date_keyboard,
    generate_port_keyboard,
    get_message,
    greeting_text_keyboard,
    language_keyboard,
)
from app.utils import get_language_enum

bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    async with get_or_create_session() as session:
        user = await user_crud.get_user(session, message.from_user.id, message.from_user.first_name.lower())
        if user and user.language is not None:
            text, keyboard = await greeting_text_keyboard(user)
            await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(
                f"Hi {message.from_user.first_name} -  {'Please choose a language.'}",
                reply_markup=await language_keyboard(),
            )


@dp.message_handler(
    lambda message: message.text
    in [
        get_message("change_language", language=Languages.UKRAINIAN.value),
        get_message("change_language", language=Languages.POLISH.value),
        get_message("change_language", language=Languages.ENGLISH.value),
    ]
)
async def handle_change_laguage(message: types.Message):
    await message.answer(f"{'Choose a language.'}", reply_markup=await language_keyboard())


@dp.message_handler(lambda message: message.text in ["English", "Ukrainian", "Polish"])
async def handle_language(message: types.Message):
    async with get_or_create_session() as session:
        user, user_created = await user_crud.get_or_create(
            UserCreateSchemas(
                chat_id=message.from_user.id,
                name=message.from_user.first_name.lower(),
                language=await get_language_enum(message.text),
            ),
            session,
        )
        if not user_created:
            user = await user_crud.update_language(
                user=user, new_lagguage=await get_language_enum(message.text), db=session
            )
        text, keyboard = await greeting_text_keyboard(user)
        await message.answer(text, reply_markup=keyboard)


@dp.message_handler(
    lambda message: message.text
    in [
        get_message("from_pl_to_se", language=Languages.UKRAINIAN.value),
        get_message("from_se_to_pl", language=Languages.UKRAINIAN.value),
        get_message("from_pl_to_se", language=Languages.POLISH.value),
        get_message("from_se_to_pl", language=Languages.POLISH.value),
        get_message("from_pl_to_se", language=Languages.ENGLISH.value),
        get_message("from_se_to_pl", language=Languages.ENGLISH.value),
    ]
)
async def handle_direction_selection(message: types.Message):
    if message.text in [
        get_message("from_pl_to_se", language=Languages.UKRAINIAN.value),
        get_message("from_pl_to_se", language=Languages.POLISH.value),
        get_message("from_pl_to_se", language=Languages.ENGLISH.value),
    ]:
        is_pl_to_se = True
    else:
        is_pl_to_se = False

    async with get_or_create_session() as session:
        if is_pl_to_se:
            country_departure = await country_crud.get_by_name(Countries.POLAND.value, session)
        else:
            country_departure = await country_crud.get_by_name(Countries.SWEDEN.value, session)
        user = await user_crud.get_user(session, message.from_user.id, message.from_user.first_name.lower())

        text, keyboard = await generate_port_keyboard(country_departure, user, session)

    await message.answer(text, reply_markup=keyboard)


@dp.message_handler(
    lambda message: re.match(
        r"^(From .* to (Sweden|Poland)|З .* до (Швеції|Польщі)|Z .* do (Swecji|Polski))$", message.text
    )
)
async def handle_port_selection(message: types.Message):
    async with get_or_create_session() as session:
        user = await user_crud.get_user(session, message.from_user.id, message.from_user.first_name.lower())
    # Get port name
    match = re.match(r"^(?:From|З|Z) (.*?) (to|do|до) (Sweden|Poland|Швеції|Польщі|Swecji|Polski)$", message.text)

    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(3)

        text, keyboard = generate_common_keyboard(selected_port, selected_country, user)

        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer("Invalid port selection format. Please choose a port.")


@dp.message_handler(
    lambda message: re.match(
        r"^(Today's ferries from .* to (Sweden|Poland)|"
        r"Сьогоднішні пароми з .* до (Швеції|Польщі)|"
        r"Dzisiejsze promy z .* do (Swecji|Polski))$",
        message.text,
    )
)
async def handle_today_ferries(message: types.Message):
    match = re.match(
        r"^(?:Today's ferries from|"
        r"Сьогоднішні пароми з|"
        r"Dzisiejsze promy z) (.*?) (to|do|до) (Sweden|Poland|Швеції|Польщі|Swecji|Polski)$",
        message.text,
    )
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(3)

        if selected_country in ["Sweden", "Швеції", "Swecji"]:
            selected_country = CountriesAbbreviatedName.SE.value
        else:
            selected_country = CountriesAbbreviatedName.PL.value

        async with get_or_create_session() as session:
            user = await user_crud.get_user(session, message.from_user.id, message.from_user.first_name.lower())

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            now = datetime.datetime.now()

            port_from = await port_crud.get_port_by_name(selected_port.lower(), session)
            country_to = await country_crud.get_by_name(
                selected_country,
                session,
            )

            ferries = await _get_ferries(port_from, country_to, now, session)

            formatted_ferries = await _format_ferries_as_string(ferries, country_to, user, session)

        main_menu = KeyboardButton("/start")
        keyboard.add(main_menu)

        await message.answer(f"{formatted_ferries}", reply_markup=keyboard)


@dp.message_handler(
    lambda message: re.match(
        r"^(Choose another departure date from .* to (Sweden|Poland)|"
        r"Oберіть iншу дату відправлення з .* до (Швеції|Польщі)|"
        r"Wybierz inna datę wylotu z .* do (Swecji|Polski))$",
        message.text,
    )
)
async def handle_choose_date(message: types.Message):
    match = re.match(
        r"^(?:Choose another departure date from|"
        r"Oберіть iншу дату відправлення з|"
        r"Wybierz inna datę wylotu z) (.*?) (to|do|до) (Sweden|Poland|Швеції|Польщі|Swecji|Polski)$",
        message.text,
    )
    if match:
        selected_port = match.group(1).lower()
        selected_country = match.group(3)
        if selected_country in ["Sweden", "Швеції", "Swecji"]:
            selected_country = CountriesAbbreviatedName.SE.value
        else:
            selected_country = CountriesAbbreviatedName.PL.value
        async with get_or_create_session() as session:
            user = await user_crud.get_user(session, message.from_user.id, message.from_user.first_name.lower())

        text, keyboard = generate_date_keyboard(selected_port, selected_country, user)
        await message.answer(
            text,
            reply_markup=keyboard,
        )
    else:
        # Todo make func for return error for all massages
        await message.answer("Invalid format")


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith(
        ("Selected date from", "Вибрана дата з", "Wybrana data wylotu z")
    )
)
async def handle_selected_date(callback_query: types.CallbackQuery):

    match = re.match(
        r"^(?:Selected date from|Вибрана дата з|Wybrana data wylotu z) (.*?) (to|do|до) "
        r"(Sweden|Poland|Швеції|Польщі|Swecji|Polski): (.*)$",
        callback_query.data,
    )
    selected_port = match.group(1).lower()
    selected_country = match.group(3)
    selected_date = match.group(4).strip()

    selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d")

    if selected_country in ["Sweden", "Швеції", "Swecji"]:
        selected_country = CountriesAbbreviatedName.SE.value
    else:
        selected_country = CountriesAbbreviatedName.PL.value

    async with get_or_create_session() as session:
        user = await user_crud.get_user(
            session, callback_query.from_user.id, callback_query.from_user.first_name.lower()
        )
        port_from = await port_crud.get_port_by_name(selected_port, session)
        country_to = await country_crud.get_by_name(
            selected_country,
            session,
        )
        ferries = await _get_ferries(port_from, country_to, selected_date, session)
        formatted_ferries = await _format_ferries_as_string(ferries, country_to, user, session)

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


async def _format_ferries_as_string(ferries: list[Ferry], country_to: Country, user: User, session: AsyncSession):
    formatted_ferries = []
    ferries = sorted(ferries, key=lambda ferry: ferry.time_departure)

    for ferry_info in ferries:
        port = await port_crud.get_port_by_id(ferry_info.port_arrival_id, session)
        port_departure = await port_crud.get_port_by_id(ferry_info.port_departure_id, session)
        country_from = await country_crud.get(session, port_departure.country_id)
        ferry_name = get_message("ferry_info_ferry_name", language=user.language.value)
        date = get_message("ferry_info_date", language=user.language.value)
        departure_time = get_message("ferry_info_departure_time", language=user.language.value)
        arrival_time = get_message("ferry_info_arrival_time", language=user.language.value)
        arrival_port = get_message("ferry_info_arrival_port", language=user.language.value)
        departure_port = get_message("ferry_info_departure_port", language=user.language.value)

        formatted_ferry = (
            f"{ferry_name}: {ferry_info.name}\n"
            f"{date}: {ferry_info.date}\n"
            f"{departure_time}: {ferry_info.time_departure}\n"
            f"{arrival_time}: {ferry_info.time_arrival}\n"
            f"{arrival_port}: {port.name.capitalize()}({country_to.name})\n"
            f"{departure_port}: {port_departure.name.capitalize()}({country_from.name})\n"
        )
        formatted_ferries.append(formatted_ferry)

    return "\n".join(formatted_ferries)


# If you want start process polling without hooks
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
