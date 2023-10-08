from __future__ import annotations

import datetime
import json
import os

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_port import port_crud
from app.models import Country, User
from app.schemas.enums import Countries

LANGUAGE_DIRECTORY = "app/telegtam_bot/languages"


def load_language(language_code):
    file_path = os.path.join(LANGUAGE_DIRECTORY, f"lang_{language_code}.json")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_message(text_key, language: str) -> str:
    language_data = load_language(language)
    text = language_data[text_key]
    return text


def generate_common_keyboard(port_departure: str, country_arrival: str, user: User) -> tuple[str, ReplyKeyboardMarkup]:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    today_str = get_message("ferries_today", language=user.language.value)
    choose_date_str = get_message("choose_date", language=user.language.value)
    today_str = today_str.replace("{country}", country_arrival.capitalize())
    today_str = today_str.replace("{port}", port_departure.capitalize())
    choose_date_str = choose_date_str.replace("{country}", country_arrival.capitalize())
    choose_date_str = choose_date_str.replace("{port}", port_departure.capitalize())

    today = KeyboardButton(today_str)
    choose_date = KeyboardButton(choose_date_str)
    main_menu = KeyboardButton("/start")
    keyboard.add(today, choose_date, main_menu)

    text = get_message("date_massage", language=user.language.value)
    text = text.replace("{country}", country_arrival.capitalize())
    text = text.replace("{port}", port_departure.capitalize())

    return text, keyboard


async def generate_port_keyboard(
    country_departure: Country, user: User, session: AsyncSession
) -> tuple[str, "ReplyKeyboardMarkup"]:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    ports = await port_crud.get_ports_by_country_id(country_departure.id, session)

    if country_departure.name.lower() == Countries.POLAND.value.lower():
        county_departure_str = Countries.POLAND.value.lower()
        country_arrival = Countries.SWEDEN.name
    else:
        county_departure_str = Countries.SWEDEN.value.lower()
        country_arrival = Countries.POLAND.name

    from_str = get_message("from", language=user.language.value)
    to_str = get_message("to", language=user.language.value)
    arrival_country_str = get_message(country_arrival.lower(), language=user.language.value)
    port_names = [
        f"{from_str} {str(port.name).capitalize()} {to_str} {arrival_country_str.capitalize()}" for port in ports
    ]

    # Add port names to the keyboard
    for name in port_names:
        keyboard.add(name)
    main_menu = KeyboardButton("/start")
    keyboard.add(main_menu)

    text = get_message("choose_port_departure", language=user.language.value)
    text = text.replace("{country}", get_message(county_departure_str, language=user.language.value))

    return text, keyboard


def generate_date_keyboard(selected_port: str, selected_country: str, user: User) -> tuple[str, "InlineKeyboardMarkup"]:
    keyboard = InlineKeyboardMarkup(row_width=2)

    today = datetime.datetime.now().date()
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        button_text = date.strftime("%Y-%m-%d")
        chosen_date_massage = get_message("chosen_date_massage", language=user.language.value)
        chosen_date_massage = chosen_date_massage.replace("{country}", selected_country.capitalize())
        chosen_date_massage = chosen_date_massage.replace("{port}", selected_port.capitalize())
        callback_massage = chosen_date_massage.replace("{date}", str(button_text))

        if i % 2 == 0:
            button = InlineKeyboardButton(
                text=f"📆 {button_text}",
                callback_data=callback_massage,
            )
        else:
            button = InlineKeyboardButton(
                text=f"📆 {button_text}",
                callback_data=callback_massage,
            )

        keyboard.insert(button)

    text = get_message("choose_date_massage", language=user.language.value)
    text = text.replace("{country}", selected_country.capitalize())
    text = text.replace("{port}", selected_port.capitalize())

    return text, keyboard


async def greeting_text_keyboard(user) -> tuple[str, ReplyKeyboardMarkup]:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    from_pl_to_se = KeyboardButton(get_message("from_pl_to_se", language=user.language.value))
    from_se_to_pl = KeyboardButton(get_message("from_se_to_pl", language=user.language.value))
    main_menu = KeyboardButton("/start")
    change_language = KeyboardButton(get_message("change_language", language=user.language.value))

    keyboard.add(from_pl_to_se, from_se_to_pl, change_language, main_menu)
    text = get_message("greeting", language=user.language.value)
    text = text.replace("{name}", user.name.capitalize())
    return text, keyboard


async def language_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    eng = KeyboardButton("English")
    ukr = KeyboardButton("Ukrainian")
    pl = KeyboardButton("Polish")
    main_menu = KeyboardButton("/start")

    keyboard.add(eng, ukr, pl, main_menu)
    return keyboard
