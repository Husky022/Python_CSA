from random import randint
from pythonping import ping
from tabulate import tabulate


def ip_adresses(quantity):
    result_list = []
    for i in range(quantity):
        el = str(str(randint(0, 255)) + '.' + str(randint(0, 255)) + '.' + str(randint(0, 255)) + '.' + str(
            randint(0, 255)))
        result_list.append(el)
    return result_list


def host_ping(ip_list):
    ip_dict = {'Reachable':[], 'Unreachable':[]}
    for el in ip_list:
        print(f'\rCheck {ip_list.index(el) + 1} of {len(ip_list)}', end='')
        response_list = ping(el)
        if response_list.success():
            ip_dict['Reachable'].append(el)
        else:
            ip_dict['Unreachable'].append(el)
    print('\r')
    return ip_dict


print(tabulate(host_ping(ip_adresses(10)), headers="keys"))