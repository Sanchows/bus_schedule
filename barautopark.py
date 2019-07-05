import requests
from bs4 import BeautifulSoup

class BarAutoPark():
    def __init__(self, num_bus = None):
        self.num_bus = num_bus


    def __str__(self):
        return str(self.num_bus)


    def get_html(self, url):
        """
        Возвращает html-код страницы.
        """

        r = requests.get(url)

        return r.text


    def get_numbers_autobus(self):
        """
        Возвращает все номера маршрутов.
        """

        numbers = []

        html = self.get_html("https://vovremia.com/baranovichi/avtobus")
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find_all('div', class_='block_bus')

        for div in divs:
            number = div.find('p', class_='font1').text.split(' ')[2]
            numbers.append(number)

        return numbers


    def get_list_napr(self):
        """
        Возвращает список направлений маршрута.
        """

        list_napr = []
        html = self.get_html(f"https://vovremia.com/baranovichi/avtobus/{self.num_bus}")
        soup = BeautifulSoup(html, 'lxml')

        naprs = soup.find('ul', class_='tabs_vov').find_all('li')
        
        for napr in naprs:
            napr_name = napr.text
            list_napr.append(napr_name)
        
        return list_napr


    def get_list_ost(self, napr):
        """
        Возвращает список названий остановок.
        
        napr - направление маршрута, int (1 or 2).       
        """

        if napr < 1 or napr > 2:
            return False

        list_ost = []
        html = self.get_html(f'https://vovremia.com/baranovichi/avtobus/{self.num_bus}')
        soup = BeautifulSoup(html, 'lxml')

        osts = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[napr-1].find('div', id='nav')
        name_osts = osts.find_all('strong')

        for ost in name_osts:
            name_ost = ost.text.strip('+')
            list_ost.append(name_ost)

        if not list_ost:
            return False
        else:
            return list_ost


    def get_all_rasp(self, napr=1):
        """
        Возвращает расписание автобуса на всех остановках маршрута.

        napr - направление маршрута, int (1 or 2).
        """

        rasp = []

        list_ost = self.get_list_ost(napr)
        
        html = self.get_html(f'https://vovremia.com/baranovichi/avtobus/{self.num_bus}')
        soup = BeautifulSoup(html, 'lxml')

        times = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[napr-1].find('div', id='nav')
        monday_sunday = times.find_all('div', class_='subnav')

        for day in monday_sunday:
            ost = list_ost[monday_sunday.index(day)]
            monday = day.find('div', class_='monday_bus').text.lstrip('Рабочие дни')
            sunday = day.find('div', class_='sunday_bus').text.lstrip('Выходные дни')
            if sunday == 'курсирует':
                sunday = 'Не курсирует'
            if monday == 'курсирует':
                monday = 'Не курсирует'

            data = {'Остановка: ': ost,
                    'Рабочие дни: ': monday,
                    'Выходные дни: ': sunday,
                }
            rasp.append(data)

        return rasp


    def get_rasp(self, list_rasp, name_ost):
        """
        Поиск по остановке.
        Возвращает расписание автобуса на остановке.

        list_rasp - список от get_all_rasp(), list.
        name_ost - название остановки, str.
        """

        for rasp in list_rasp:
            if rasp['Остановка: '] == name_ost:
                return rasp

        return False