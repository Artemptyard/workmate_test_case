import subprocess
import sys


# Файл для тестов
FILE_PATH = "data/products.csv"


def run_script(*args):
    """Запуск скрипта в отдельном процессе с передачей аргументов."""
    return subprocess.run(
        [sys.executable, "main.py", *args],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )


def test_file_required():
    """Проверка запуска без указания файла."""
    result = run_script("--where", "price>10")
    assert result.returncode != 0
    assert "the following arguments are required: --file" in result.stderr.lower()


def test_filter():
    """Проверка фильтра."""
    result = run_script("--file", FILE_PATH, "--where", "rating>4.7")
    assert "apple" in result.stdout
    assert "xiaomi" not in result.stdout


def test_order_by_desc():
    """Проверка сортировки по убыванию."""
    result = run_script("--file", FILE_PATH, "--order-by", "price=desc")
    assert result.stdout.index("apple") < result.stdout.index("samsung")


def test_aggregate_avg():
    """Проверка вычисления среднего для оценки."""
    result = run_script("--file", FILE_PATH, "--aggregate", "rating=avg")
    assert "rating_mean" in result.stdout


def test_aggregate_excludes_order():
    """Проверка выполнения агрегации и отмена выполнения сортировки."""
    result = run_script("--file", FILE_PATH, "--aggregate", "price=max", "--order-by", "brand=asc")
    assert "Warning" in result.stdout
    assert "price_max" in result.stdout


def test_invalid_filter_format():
    """Проверка передачи неправильного фильтра."""
    result = run_script("--file", FILE_PATH, "--where", "invalid-filter-format")
    assert result.returncode != 0
    assert "Неверный формат условия" in result.stderr


def test_invalid_operator_in_filter():
    """Проверка передачи неподдерживаемой операции фильтрации."""
    result = run_script("--file", FILE_PATH, "--where", "rating!4")
    assert result.returncode != 0
    assert "Неверный формат условия" in result.stderr


def test_unknown_argument():
    """Проверка запуска с неизвестным аргументом."""
    result = run_script("--file", FILE_PATH, "--unknown", "value")
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr


def test_aggregate_invalid_function():
    """Проверка передачи неподдерживаемой операции агрегации."""
    result = run_script("--file", FILE_PATH, "--aggregate", "price=total")
    assert result.returncode != 0
    assert "Неподдерживаемая агрегация" in result.stderr


def test_sort_invalid_direction():
    """Проверка передачи неподдерживаемой сортировки."""
    result = run_script("--file", FILE_PATH, "--order-by", "brand=sideways")
    assert result.returncode != 0
    assert "Неподдерживаемая сортировка" in result.stderr


def test_invalid_column_for_aggregation():
    """Проверка передачи неподдерживаемой сортировки."""
    result = run_script("--file", FILE_PATH, "--aggregate", "brand=avg")
    assert result.returncode != 0
    assert "не может быть преобразовано в число" in result.stderr
