import datetime

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.crud.crud_port import port_crud
from app.schemas.enums import Countries, CountriesAbbreviatedName


def generate_common_keyboard(port_departure, country_arrival):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    today = KeyboardButton(f"Today from {port_departure.capitalize()} to {country_arrival}")
    choose_date = KeyboardButton(f"Choose a date from {port_departure.capitalize()} to {country_arrival}")
    main_menu = KeyboardButton("/start")

    keyboard.add(today, choose_date, main_menu)
    return keyboard


async def generate_port_keyboard(country_departure, session):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    ports = await port_crud.get_ports_by_country_id(country_departure.id, session)

    if country_departure.name.lower() == Countries.POLAND.value.lower():
        country_arrival = CountriesAbbreviatedName.SE.name
    else:
        country_arrival = CountriesAbbreviatedName.PL.name

    port_names = [f"From {str(port.name).capitalize()} to {country_arrival}" for port in ports]

    # Add port names to the keyboard
    for name in port_names:
        keyboard.add(name)
    main_menu = KeyboardButton("/start")
    keyboard.add(main_menu)
    return keyboard


def generate_date_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=7)
    today = datetime.datetime.now().date()
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        button_text = date.strftime("%Y-%m-%d")
        button_callback = f"select_date:{date}"
        keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=button_callback))
    return keyboard
