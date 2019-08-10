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
            if number == '24' or number == '27':
                continue

            numbers.append(number)

        return numbers


    def get_list_dirs(self):
        """
        Возвращает список направлений маршрута.
        """

        list_directions = []
        html = self.get_html(f"https://vovremia.com/baranovichi/avtobus/{self.num_bus}")
        soup = BeautifulSoup(html, 'lxml')

        directions = soup.find('ul', class_='tabs_vov').find_all('li')
        
        for direction in directions:
            direction_name = direction.text
            list_directions.append(direction_name)
        
        return list_directions


    def get_list_ost(self, direction):
        """
        Возвращает список названий остановок.
        
        direction - направление маршрута, int (1 or 2).       
        """

        if direction < 1 or direction > 2:
            return False

        list_ost = []
        html = self.get_html(f'https://vovremia.com/baranovichi/avtobus/{self.num_bus}')
        soup = BeautifulSoup(html, 'lxml')
        
        if int(self.num_bus) == 26: # special page layout
            osts = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[direction-1].find_all('strong')
            for ost in osts:
                list_ost.append(ost.text)

        else:
            osts = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[direction-1].find('div', id='nav')
            name_osts = osts.find_all('strong')

            for ost in name_osts:
                name_ost = ost.text.strip('+')
                list_ost.append(name_ost)
            

        if not list_ost:
            return False
        else:
            return list_ost


    def get_all_rasp(self, direction=1):
        """
        Возвращает расписание автобуса на всех остановках маршрута.

        direction - направление маршрута, int (1 or 2).
        """

        rasp = []
        list_ost = self.get_list_ost(direction)

        html = self.get_html(f'https://vovremia.com/baranovichi/avtobus/{self.num_bus}')
        soup = BeautifulSoup(html, 'lxml')
        if int(self.num_bus) == 26: # special page layout
            times = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[direction-1].find('div')
            monday_sunday = times.find_all('div')[-2:]
            ost = list_ost[0]
            monday = monday_sunday[0].text.lstrip('Рабочие дни')
            sunday = monday_sunday[1].text.lstrip('Выходные дни')

            if sunday == 'курсирует':
                sunday = 'Не курсирует'
            if monday == 'курсирует':
                monday = 'Не курсирует'

            data = {'Остановка: ': ost,
                    'Рабочие дни: ': monday,
                    'Выходные дни: ': sunday,
                }
            rasp.append(data)
        
        elif int(self.num_bus) == 27: # special page layot (page is not have div block 'monday_bus' and 'sunday_bus')
            pass

        else:
            times = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[direction-1].find('div', id='nav')
            monday_sunday = times.find_all('div', class_='subnav')

            for day in monday_sunday:
                ost = list_ost[monday_sunday.index(day)]
                monday = day.find('div', class_='monday_bus').text.lstrip('Рабочие дни')
                sunday = day.find('div', class_='sunday_bus').text.lstrip('Выходные дни')
                if sunday == 'курсирует':
                    sunday = 'Не курсирует'
                if monday == 'курсирует':
                    monday = 'Не курсирует'
                
                if self.num_bus == '1': # very bad layout !!! >_<
                    monday = monday.rstrip('Выделенный рейс следует до кл. Русино')

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

    def find_nearest(self, time_now, list_rasp):
        if 'Не курсирует' in list_rasp[0]:
            return None

        time_now_hours = time_now.split(':')[0]
        time_now_mins = time_now.split(':')[1]
        time_now_new = int(time_now_hours + time_now_mins)

        for time in list_rasp:
            hours = time.split(':')[0]
            mins = time.split(':')[1]

            time_depart = int(hours + mins)
            
            if time_depart < time_now_new:
                continue

            elif time_depart == time_now_new:
                return 'Отправляется прямо сейчас'

            elif time_depart > time_now_new:
                return f'{hours}:{mins}'

        return 'На сегодня нет автобусов'