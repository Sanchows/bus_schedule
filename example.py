from barautopark import BarAutoPark


def main():

    numbers = BarAutoPark().get_numbers_autobus()
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

        bus = BarAutoPark(num_bus = number_autobus)

        list_dirs = bus.get_list_dirs()
        print('\n\tНаправления:')
        for dirc in list_dirs:
            print('\t{0}: {1}'.format(list_dirs.index(dirc)+1, dirc))
    
        while True:
            dirc = int(input("Направление (1 или 2): "))
            list_ost = bus.get_list_ost(dirc)

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

    list_rasp = bus.get_all_rasp(dirc)
    rasp = bus.get_rasp(list_rasp, ost)
    
    if not rasp:
       print('Расписание не найдено.')
       return

    for key, value in rasp.items():
        print(key, value)

if __name__ == "__main__":
    while True:
        print ('\n\tНомера автобусов:')
        main()
            
        repeat = input("1 - продолжить , 'любой_другой_символ' - выход")
        if repeat == '1':
            continue
        else:
            break
