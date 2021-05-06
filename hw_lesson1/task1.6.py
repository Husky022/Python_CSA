with open('test.txt') as f:
    print(f'{f.encoding} - Кодировка по умолчанию', end='\n\n')

with open('test.txt', encoding='utf-8') as f:
    for line in f:
        print(line)