from tabulate import tabulate
from typing import Dict, Iterator
from csv import DictReader


def get_dict_from_csv(file: str) -> Iterator[Dict]:
    """Получение списка словарей из CSV файла.

    :param file: путь к файлу.
    :return: Итератор всех строк файла как Dict.
    """
    with open(file, 'r', encoding='utf-8') as f:
        dict_reader = DictReader(f)
        for row in dict_reader:
            yield row


def print_table(data: Iterator[Dict]):
    """Вывод данных в виде таблицы.

    :param data: Список словарей, ключи которых будут заголовком таблицы.
    """
    table = tabulate(data, headers="keys", tablefmt="fancy_grid")
    if not table:
        print("Ничего")
    print(table)


if __name__ == "__main__":
    test_data = get_dict_from_csv("../data/products.csv")
    print_table(test_data)
