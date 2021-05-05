import yaml

first_key = ['item1', 'item2', 'item3', 'item4', 'item5',]

second_key = 777

third_key = {'£': 'item1', '¥': 'item2', '©': 'item3', '®': 'item4', 'µ': 'item5' }

data_to_yaml = {'first_key':first_key, 'second_key':second_key, 'third_key':third_key}

with open('file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data_to_yaml, f, default_flow_style=False, allow_unicode=True)

