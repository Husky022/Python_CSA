words = ['attribute', 'класс', 'функция', 'type']

for word in words:
    try:
        print(word.encode('ascii'))
    except UnicodeEncodeError:
        print(f'{word} - нельзя записать в байтовом типе ')
