from pythonping import ping


def ip_adresses(start_range, end_range):
    result_list = []
    for i in range(start_range, end_range):
        el = '125.235.169.' + str(i)
        result_list.append(el)
    return result_list


def host_ping(ip_list):
    for line in ip_list:
        response_list = ping(line)
        if response_list.success():
            print(line + ' - Reachable')
        else:
            print(line + ' - Unreachable')
host_ping(ip_adresses(150, 160))
