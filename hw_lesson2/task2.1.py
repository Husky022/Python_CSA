import re
import csv

new_files = ['info_1.txt', 'info_2.txt', 'info_3.txt',]
new_parametres = ['Название ОС', 'Код продукта', 'Изготовитель системы', 'Тип системы']


def pattern(parametres):
    current_pattern = '('
    for el in parametres:
        current_pattern += str(el) + '|'
    return  current_pattern[:-1] + ')'

def get_data(file_list, parametres):
    data=[]
    for file in file_list:
        with open(file) as f:
            data_element = [re.split('\s{4,}', el)[1].rstrip() for el in f.readlines() if re.findall(pattern(parametres), el)]
            data.append(data_element)
    return data


def write_to_csv(parametres, file_list):
    with open('report.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(parametres)
    with open('report.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerows(get_data(file_list, parametres))


write_to_csv(new_parametres, new_files)



