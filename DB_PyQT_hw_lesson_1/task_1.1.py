from random import randint
from pythonping import ping


def ip_adresses(quantity):
    result_list = []
    for i in range(quantity):
        el = str(str(randint(0, 255)) + '.' + str(randint(0, 255)) + '.' + str(randint(0, 255)) + '.' + str(
            randint(0, 255)))
        result_list.append(el)
    return result_list


def host_ping(ip_list):
    with open('ip_adresses.txt', 'w') as f:
        for line in ip_list:
            response_list = ping(line)
            if response_list.success():
                f.write(line + ' - Reachable\n')
            else:
                f.write(line + ' - Unreachable\n')


host_ping(ip_adresses(10))

