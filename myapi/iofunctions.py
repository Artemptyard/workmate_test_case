from tabulate import tabulate
from typing import List, Dict
from csv import DictReader


def get_list_from_csv(file: str) -> List[Dict]:
    """Получение списка словарей из CSV файла.

    :param file: путь к файлу.
    """
    with open(file, 'r', encoding='utf-8') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
    return list_of_dict


def print_table(data: List[Dict]):
    """Вывод данных в виде таблицы.

    :param data: Список словарей, ключи которых будут заголовком таблицы.
    """
    table = tabulate(data, headers="keys", tablefmt="fancy_grid")
    if not table:
        print("Ничего")
    print(table)


if __name__ == "__main__":
    test_data = get_list_from_csv("../data/products.csv")
    print_table(test_data)
