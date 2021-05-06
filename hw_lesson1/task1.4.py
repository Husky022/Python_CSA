words = ['разработка', 'администрирование', 'protocol', 'standard']

for word in words:
    try:
        word_byte = word.encode('ascii')
        print(f'{word}: Преобразование - {word_byte};', end=' ')
        word_str =  word_byte.decode('ascii')
        print(f'Обратное преобразование - {word_str}')
    except UnicodeEncodeError:
        print(f'{word} - нельзя записать в байтовом типе ')