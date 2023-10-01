from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.crud.crud_country import country_crud
from app.crud.crud_ferry import ferry_crud
from app.crud.crud_port import port_crud
from app.schemas.ferry_schemas import FerryCreateSchemas
from app.utils import get_country_from_city, replace_polish_chars


class Parser:
    polferies_url = "https://polferries.pl/cargo/rozklad.html?code=sy"

    async def _get_html(self, url) -> BeautifulSoup:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        return soup

    async def parser_polferries(self, db):
        """Parser timetable https://polferries.pl/cargo/rozklad.html?code=sy"""

        response = []
        soup = await self._get_html(self.polferies_url)

        find_month = soup.find("ul", class_="nav nav-tabs")
        month = []

        for items in find_month:
            month.append(items.get_text())

        month_list = []

        for i in month:  # выделяем в словарь месяц и год
            month_in_polish = {
                "Styczeń": 1,
                "Luty": 2,
                "Marzec": 3,
                "Kwiecień": 4,
                "Maj": 5,
                "Czerwiec": 6,
                "Lipiec": 7,
                "Sierpień": 8,
                "Wrzesień": 9,
                "Październik": 10,
                "Listopad": 11,
                "Grudzień": 12,
            }
            word = "".join(" " if el.isdigit() else el for el in i).split()
            number = "".join(el if el.isdigit() else " " for el in i).split()
            word = month_in_polish[word[0]]

            month_list.append([word, number[0]])

        name_of_ferry_dir = {"BAL": "Baltivia", "CRA": "Cracovia", "MAZ": "Mazovia"}
        find_all_table = soup.find_all("div", class_="tab-content")  # выделяем 2 таблицы

        for div_num in range(len(find_all_table)):
            find_all_month = find_all_table[div_num].find_all("div", class_="panel-collapse")  # находим месяца
            for month_num in range(len(find_all_month)):
                all_str_table = (
                    find_all_month[month_num].find("table", class_="rozklad-tabela").find_all("tr")
                )  # в каждой таблице выделяем строки
                for one_str_of_table_num in range(len(all_str_table)):  # проходим строки таблицы
                    if one_str_of_table_num == 1:
                        arrival_sailing = all_str_table[one_str_of_table_num].find("td")
                        arrival_sailing = arrival_sailing.get_text()
                        arrival_sailing = arrival_sailing.split("-")
                        arrival = arrival_sailing[1].replace(" ", "").lower()
                        sailing = arrival_sailing[0].replace(" ", "").lower()

                        arrival = replace_polish_chars(arrival)
                        sailing = replace_polish_chars(sailing)

                        try:
                            arrival_port = await self.create_port(arrival, db)
                            sailing_port = await self.create_port(sailing, db)
                        except:
                            continue
                    if one_str_of_table_num >= 2:
                        date_time_ferry = all_str_table[one_str_of_table_num].find_all("td")
                        for day in range(len(date_time_ferry)):  # проходим дни по каждой строке таблицы
                            if day == 0:  # находим время прибытия отплытия
                                time_arrival_sailing = date_time_ferry[day].get_text().split(" - ")
                                time_arrival = time_arrival_sailing[1]
                                time_sailing = time_arrival_sailing[0]

                            else:  # при наличии создаем обьект
                                if date_time_ferry[day].get_text():
                                    name_one = date_time_ferry[day].get_text()
                                    try:
                                        date_ferry = (
                                            f"{str(month_list[month_num][1]).zfill(2)}-"
                                            f"{str(month_list[month_num][0]).zfill(2)}-"
                                            f"{str(day).zfill(2)}"
                                        )
                                        date_ferry = datetime.strptime(date_ferry, "%Y-%m-%d")
                                        name_ferry = name_of_ferry_dir[name_one]
                                    except KeyError:
                                        continue
                                    ferry = await ferry_crud.create_ferry(
                                        FerryCreateSchemas(
                                            name=name_ferry,
                                            date=date_ferry,
                                            time_departure=time_sailing,
                                            time_arrival=time_arrival,
                                            port_departure_id=sailing_port.id,
                                            port_arrival_id=arrival_port.id,
                                        ),
                                        db,
                                    )
                                    response.append(ferry)
                                    # print(name_ferry, date_ferry , time_sailing, time_arrival, sailing, arrival)
                                    # a = Ferry.objects.create(
                                    #     name=name_ferry,
                                    #     date=date_ferry,
                                    #     time_departure=time_sailing,
                                    #     time_arrival=time_arrival,
                                    #     port_departure=sailing,
                                    #     port_arrival=arrival,
                                    # )
                                    # a.save()
        return response

    async def create_port(self, city: str, db):
        country, abbreviation = await get_country_from_city(city)
        country = await country_crud.get_or_create(country, abbreviation, db)
        print(country)
        port = await port_crud.get_or_create_by_name(city, country.id, db)
        return port
