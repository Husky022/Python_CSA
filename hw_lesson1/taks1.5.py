import subprocess

args = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]

for el in args:
    subproc_ping = subprocess.Popen(el, stdout=subprocess.PIPE)

    for line in subproc_ping.stdout:
                line = line.decode('cp866').encode('utf-8')
                print(line.decode('utf-8'))
