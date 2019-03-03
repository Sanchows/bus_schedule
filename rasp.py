import requests, sys
from bs4 import BeautifulSoup

def get_html(url):
    r = requests.get(url)
    return r.text

def get_list_napr(html):
    list_napr = []
    soup = BeautifulSoup(html, 'lxml')
    naprs = soup.find('ul', class_='tabs_vov').find_all('li')
    for napr in naprs:
        napr_name = napr.text
        list_napr.append(napr_name)
    return list_napr

def get_list_ost(html, napr):
    """Получает список названий остановок"""
    if napr < 1 or napr > 2:
        return False
    list_ost = []
    soup = BeautifulSoup(html, 'lxml')
    osts = soup.find('div', class_='rasp_huk').find_all('div', class_='tab_box')[napr-1].find('div', id='nav')
    name_osts = osts.find_all('strong')

    for ost in name_osts:
        name_ost = ost.text.strip('+')
        list_ost.append(name_ost)
    return list_ost

def get_rasp(html, napr=1):
    """Получает расписание"""
    list_ost = get_list_ost(html, napr)
    if not list_ost:
        return False
    rasp = []
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
                'Выходные дни: ': sunday
        }
        rasp.append(data)
    return rasp

def search_ost(list_rasp, ostanovka):
    for rasp in list_rasp:
        for key, value in rasp.items():
            if key == 'Остановка: ' and value == ostanovka:
                data = []
                for key, value in rasp.items():
                    data.append(key + value)
                return data
    
    return False

def get_numbers_autobus():
    numbers = []
    soup = BeautifulSoup(get_html("https://vovremia.com/baranovichi/avtobus"), 'lxml')
    divs = soup.find('div', class_ = 'content_right').find_all('div', class_='block_bus')
    for div in divs:
        number = div.find('p', class_='font1').text.split(' ')[2]
        numbers.append(number)
    return numbers

def main():
    numbers = get_numbers_autobus()
    base_url = "https://vovremia.com/baranovichi/avtobus/"
    
    while True:
        b=0
        while b < len(numbers)+6:  
            for i in numbers[b:b+6]:
                print(i, end='\t')
            print()
            b+=6

        number_autobus = input("Номер автобуса: ")
        if number_autobus not in numbers:
            continue
        html = get_html(base_url + number_autobus)

        list_napr = get_list_napr(html)
        print('\n\tНаправления:')
        for napr in list_napr:
            print('\t{0}: {1}'.format(list_napr.index(napr)+1, napr))
    
        while True:
            napr = int(input("Направление (1 или 2): "))
            list_ost = get_list_ost(html, napr)
            if not list_ost:
                continue

            print('\n\tСписок остановок:')
            for ost in list_ost:
                print ('\t{0}: {1}'.format(list_ost.index(ost)+1, ost))
            while True:
                number_ost = int(input("Номер остановки: "))
                if number_ost < 1 or number_ost > len(list_ost):
                    continue
                ost = list_ost[number_ost-1]
                if ost in list_ost:
                    break
            break
        break

    list_rasp = get_rasp(html, napr)
    rasp = search_ost(list_rasp, ost)
    if not rasp:
       return
    print('\n{0}\n{1}\n{2}'.format(rasp[0].title(), rasp[1], rasp[2]))

if __name__ == "__main__":
    while True:
        print ('\n\tНомера автобусов:')
        main()
            
        repeat = input("1 - продолжить , 'любой_другой_символ' - выход")
        if repeat == '1':
            continue
        else:
            break