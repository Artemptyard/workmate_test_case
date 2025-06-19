from typing import List, Dict, Tuple, Any, Iterator, Callable
from statistics import mean
import re
import operator


# Поддерживаемые операции для фильтрации (where)
ALLOWED_OPS = {
    '=': operator.eq,
    '<': operator.lt,
    '>': operator.gt,
}

# Поддерживаемые операции для агрегации (aggregate)
ALLOWED_AGGS = {
    'avg': mean,
    'min': min,
    'max': max,
}


def parse_condition(condition: str, allowed_ops: str) -> tuple:
    """Проверка и разделение условия."""
    match = re.match(rf'^(.*?)\s*([{re.escape(allowed_ops)}])\s*(.*?)$', condition)
    if not match:
        raise ValueError(f"Неверный формат условия: {condition}")
    return match.groups()


class MyFilter:
    def __init__(self, condition: str):
        self.col, self.op, self.value = self.parse_condition(condition)
        self._filter_format = "{}" + f"{self.op}{self.value}"

    @staticmethod
    def parse_condition(condition: str) -> Tuple[str, str, str]:
        """Разбивает строку фильтра на (столбец, операция, значение).
        Поддерживает операции: '=', '>', '<'.

        :param condition: Условие фильтрации (пр. "rating>4").
        """
        global ALLOWED_OPS
        column, op, value = parse_condition(condition, ''.join(ALLOWED_OPS.keys()))
        return column.strip(), op, value.strip()

    def _filter(self, line: Dict[str, Any]) -> bool:
        """Проверка соответствия строки фильтру."""
        global ALLOWED_OPS
        left = line[self.col]
        right = self.value
        # Попытка приведения к числу
        try:
            left = float(left)
            right = float(right)
        except ValueError:
            pass

        return ALLOWED_OPS[self.op](left, right)

    def filter(self, line: Dict[str, Any]) -> bool:
        """Проверка соответствия строки фильтру."""
        try:
            if self.col not in line:
                raise KeyError(f"Колонка '{self.col}' отсутствует в данных.")
            return self._filter(line)
        except Exception as e:
            raise ValueError(f"Ошибка фильтрации строки: {line}\n{e}")


def handle_filter(data: Iterator[dict], condition: str) -> Iterator[dict]:
    """Применение фильтрации к данным.

    :param data: Данные, для которых применяется фильтр.
    :param condition: Условие фильтрации.
    :return: Данные после фильтрации.
    """
    try:
        my_filter = MyFilter(condition)
        return filter(my_filter.filter, data)
    except Exception as e:
        raise ValueError(f"Ошибка в фильтрации: {e}")


class MyAggregator:
    def __init__(self, condition: str):
        self.column, self._func = self.parse_condition(condition)
        self.values = []

    @staticmethod
    def parse_condition(condition: str) -> Tuple[str, Callable]:
        """Разбивает строку фильтра на (столбец, операция).

        :param condition: Условие агрегации (пр. "rating=avg").
        """
        global ALLOWED_AGGS
        col, _, agg = parse_condition(condition, "=")
        if agg not in ALLOWED_AGGS:
            raise ValueError(f"Неподдерживаемая агрегация: {agg}")
        return col.strip(), ALLOWED_AGGS[agg]

    def _consume(self, row: Dict[str, Any]):
        """Запись значений для агрегации."""
        try:
            if self.column not in row:
                raise KeyError(f"Колонка '{self.column}' не найдена.")
            value = float(row[self.column])
            self.values.append(value)
        except ValueError:
            raise ValueError(f"Значение '{row[self.column]}' не может быть преобразовано в число.")
        except Exception as e:
            raise ValueError(f"Ошибка при агрегации строки: {row}\n{e}")

    def aggregate(self, data: Iterator[Dict]) -> List[Dict]:
        """Получение результата агрегации."""
        for row in data:
            self._consume(row)
        try:
            return [{f"{self.column}_{self._func.__name__}": self._func(self.values)}]
        except Exception as e:
            raise ValueError(f"Ошибка при вычислении агрегации: {e}")


def handle_aggregate(data: Iterator[dict], condition: str) -> List[dict]:
    """Применение агрегации к данным.

   :param data: Данные, для которых применяется агрегация.
   :param condition: Условие агрегации.
   :return: Результат агрегации.
   """
    try:
        my_aggr = MyAggregator(condition)
        return my_aggr.aggregate(data)
    except Exception as e:
        raise ValueError(f"Ошибка агрегации: {e}")


def handle_order(data: Iterator[dict], condition: str) -> List[dict]:
    """Применение сортировки к данным.

   :param data: Данные, которые нужно отсортировать.
   :param condition: Условие сортировки.
   :return: Отсортированные данные.
   """
    try:
        key, _, order = parse_condition(condition, "=")
        order = order.lower()
        if order in ["asc", "desc"]:
            reverse = order.strip().lower() == 'desc'
        else:
            raise Exception(f"Неподдерживаемая сортировка: {order}")
        return sorted(data, key=lambda row: row[key], reverse=reverse)
    except KeyError:
        raise ValueError(f"Колонка '{key}' отсутствует в данных.")
    except Exception as e:
        raise ValueError(f"Ошибка сортировки: {e}")
