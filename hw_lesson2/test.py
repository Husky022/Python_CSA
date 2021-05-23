import csv

# with open('username.csv', encoding='utf-8') as f:
#     reader = csv.reader(f, delimiter = ";")
#     headers = next(reader)
#     print('headers', headers)
#     for line in reader:
#         print(line)


# data = [['Username', 'Identifier', 'First name', 'Last name'],
# ['booker12', '9012', 'Rachel', 'Booker'],
# ['grey07', '2070', 'Laura', 'Grey'],
# ['johnson81', '4081', 'Craig', 'Johnson'],
# ['jenkins46', '9346', 'Mary', 'Jenkins'],
# ['smith79', '5079', 'Jamie', 'Smith']]
#
# with open('username2.csv', 'w', encoding='utf-8', newline='') as f:
#     writer = csv.writer(f, delimiter = ";", quoting=csv.QUOTE_NONNUMERIC)
#     for line in data:
#         writer.writerow(line)
#
# with open('username2.csv', encoding='utf-8') as f:
#     reader = csv.reader(f, delimiter = ";")
#     for line in reader:
#         print(line)

with open('info_1.txt') as f:
    print(f.readlines())