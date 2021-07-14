import subprocess


num_clients = 10

for i in range(num_clients):
    p = subprocess.Popen(["py", "client.py"], cwd='../hw_lesson3')




