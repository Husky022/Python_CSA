words = ['разработка', 'сокет', 'декоратор']

for word in words:
    word_bytes = word.encode('utf-8')
    print(f'{word} - {type(word)}')
    print(f'{word_bytes} - {type(word_bytes)}')

