import json
import time


def write_order_to_json(item, quantity, price, buyer):
    dict_to_order = dict(item=item, quantity=quantity, price=price, buyer=buyer, date=time.ctime())
    data = json.load(open('orders.json', encoding='utf-8'))
    data['orders'].append(dict_to_order)
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


write_order_to_json('Кроссовки', 2, 250, 'Lola')