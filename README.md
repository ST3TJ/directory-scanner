# Directory Scanner

Directory Scanner — простой скрипт на Python для сканирования директорий и сбора информации о файлах и папках, включая BLAKE3 хэш файлов. Результаты сохраняются в JSON файл.

## Установка

1. Склонируйте репозиторий:

```
git clone https://github.com/yourusername/directory-scanner.git
```

2. Перейдите в папку проекта:

```
cd directory-scanner
```

3. Установите зависимости:

```
pip install -r requirements.txt
```

## Использование

### Через CLI

Сканирование директории с указанием пути и сохранением результата:

```
python scanner.py --dir "C:\Path\To\Scan" --out "output.json" --depth 3
```

- `--dir` — директория для сканирования (если не указано, откроется диалог выбора).
- `--out` — путь для сохранения JSON файла (если не указано, откроется диалог сохранения).
- `--depth` — глубина рекурсивного сканирования (по умолчанию 3).
- `--version` — вывод версии скрипта.

### Через диалог

Если не указывать `--dir` или `--out`, откроются стандартные диалоги выбора директории и файла для сохранения.  

## Пример JSON вывода

```
{
    "example_file.txt": {
        "type": "file",
        "path": "C:\\Path\\To\\Scan\\example_file.txt",
        "name": "example_file.txt",
        "size": 1234,
        "creation_time": 1699999999.0,
        "last_modified_time": 1699999999.0,
        "crc": "abc123..."
    },
    "example_folder": {
        "type": "directory",
        "path": "C:\\Path\\To\\Scan\\example_folder",
        "name": "example_folder",
        "total_size": 5678,
        "file_count": 2,
        "subdir_count": 1,
        "creation_time": 1699999999.0,
        "last_modified_time": 1699999999.0,
        "children": { ... }
    }
}
```

## Зависимости

- Python 3.8+
- blake3
- tqdm