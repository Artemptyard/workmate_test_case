import argparse
from typing import Dict, Tuple, Any, Iterator

from myapi.iofunctions import get_list_from_csv, print_table
from myapi.handlers import handle_filter, handle_order, handle_aggregate


def interpreter(data: Iterator[dict] = None, **kwargs) -> Tuple[Iterator[dict], Dict[str, Any]]:
    """Применение аргумента для обработки данных.

    :param data: Данные для обработки.
    :param kwargs: Аргументы командной строки.
    :return: Обработанные данные.
    """
    # Использования match/case в данном случае обусловлено тем,
    # что в случае добавления новых функций может возникнуть необходимость
    # применения двух разных аргументов одновременно.
    match kwargs:
        case {"file": str(file), **remain_actions}:
            data = get_list_from_csv(file)
            return data, remain_actions
        case {'where': str(condition), **remain_actions}:
            data = handle_filter(data, condition)
            return data, remain_actions
        case {'order_by': str(condition), **remain_actions}:
            data = handle_order(data, condition)
            return data, remain_actions
        case {'aggregate': str(condition), **remain_actions}:
            data = handle_aggregate(data, condition)
            return data, remain_actions
        case _:
            raise SyntaxError(f"Неизвестный аргумент: {kwargs}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Простой обработчик CSV файлов.")
    # Группа обязательных аргументов
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        "--file", "-f",
        required=True,
        help="Путь к CSV-файлу."
    )

    # Группа необязательных аргументов
    optional = parser.add_argument_group('optional action arguments')

    optional.add_argument(
        "--where",
        help=("""
            Фильтрация по колонке. Формат: "имя_колонки<значение", "имя_колонки>значение", "имя_колонки=значение". 
            Примеры: "rating>4", "brand=apple".
        """)
    )
    optional.add_argument(
        "--aggregate",
        help=("""
            Агрегация по колонке. Формат: "имя_колонки=операция". 
            Операции: avg, min, max. 
            Примеры: "rating=avg", "price=max".
        """)
    )
    optional.add_argument(
        "--order-by",
        help=("""
            Сортировка по колонке. Формат: "имя_колонки=asc" или "имя_колонки=desc". 
            Примеры: "brand=asc", "price=desc".
        """)
    )

    return parser.parse_args()


def remove_none(data: dict) -> dict:
    """Убрать все элементы, где значение None."""
    return {k: v for k, v in data.items() if v is not None}


def main():
    args = parse_args()
    dict_args = remove_none(vars(args))

    # Убираем лишнее действие при агрегации
    if dict_args.get("aggregate") and dict_args.get("order_by"):
        order = dict_args.pop("order_by")
        print(f"Warning: Действие --aggregate исключает действие --order_by ({order})!")

    result = []
    while dict_args:
        result, dict_args = interpreter(result, **dict_args)

    print_table(result)


if __name__ == "__main__":
    main()
