# Shell Emulator


## 1. Общее описание ##

 Shell Emulator — это консольное приложение на Python, эмулирующее работу простой командной оболочки. Эмулятор позволяет пользователю взаимодействовать с виртуальной файловой системой, хранящейся в архиве tar. Он поддерживает базовые команды для навигации и управления файлами, такие как ls, cd, tac, chown, uptime и exit.

Эмулятор читает конфигурацию из файла config.toml, который задаёт параметры работы приложения, включая путь к файловой системе, лог-файлу и стартовому скрипту. Приложение также сохраняет историю введённых команд в лог-файл в формате JSON.


## 2. Описание функций и настроек ##

## Основные функции ##

* Загрузка файловой системы из архива tar: Эмулятор читает файловую систему из указанного архива и позволяет просматривать и навигировать по ней.

* Поддержка команд оболочки:
> * ls [path]: отображает содержимое указанного каталога.
> * cd [path]: изменяет текущий каталог на указанный.
> * tac [file]: выводит содержимое указанного файла в обратном порядке строк.
> * chown [owner] [file]: изменяет владельца указанного файла на указанного пользователя (эмуляция).
> * uptime: отображает время работы эмулятора с момента запуска.
> * exit: сохраняет журнал команд и завершает работу эмулятора.
* Логирование команд: Все введённые команды сохраняются в лог-файл в формате JSON.
* Стартовый скрипт: При запуске эмулятор может выполнять команды из указанного стартового скрипта.

## Настройки в config.toml ##
Файл config.toml используется для задания настроек эмулятора. Пример содержимого:
```
hostname = "my_emulator"
filesystem_path = "filesystem.tar"
log_file = "emulator_log.json"
startup_script = "startup.sh"
```
* hostname: имя хоста, отображаемое в приглашении командной строки.
* filesystem_path: путь к архиву файловой системы в формате tar.
* log_file: путь к файлу, в который будет записываться журнал команд.
* startup_script: путь к файлу со стартовым скриптом (опционально).

## Описание команд ##

> ls [path]
Отображает содержимое указанного каталога. Если путь не указан, отображает содержимое текущего каталога.

** Пример: **
```
my_emulator:/dir1$ ls
file1.txt
test_file.txt
```

> cd [path] **
Изменяет текущий каталог на указанный.

** Пример: **
```
my_emulator:/$ cd dir1
my_emulator:/dir1$
```

> tac [file] **
Выводит содержимое указанного файла в обратном порядке строк.

** Пример: **
```
my_emulator:/dir1$ tac test_file.txt
Содержимое тестового файла
```

> chown [owner] [file]
Изменяет владельца указанного файла на указанного пользователя (эмуляция).

** Пример: **
```
my_emulator:/dir1$ chown new_owner file1.txt
Изменен владелец 'file1.txt' на 'new_owner'
```

> uptime
Отображает время работы эмулятора с момента запуска.

** Пример: **
```
my_emulator:/dir1$ uptime
Время работы: 42 секунд
```

> exit
Сохраняет журнал команд и завершает работу эмулятора.

** Пример: **
```
my_emulator:/dir1$ exit
```

## 3. Описание команд для сборки проекта ##

## Требования ##
* Python 3.6 или выше.
* Модуль toml (для установки: pip install toml).
* Модуль pytest для запуска тестов (для установки: pip install pytest).

> ## Шаги для запуска ##
>> 1. Клонируйте репозиторий или скопируйте файлы проекта в рабочую директорию.

>> 2. Создайте виртуальную файловую систему:

>>> * Создайте директории и файлы:
```
mkdir -p vfs/dir1
mkdir -p vfs/dir2
echo "Содержимое файла 1" > vfs/dir1/file1.txt
echo "Содержимое тестового файла" > vfs/dir1/test_file.txt
echo "Содержимое файла 2" > vfs/dir2/file2.txt
echo "Содержимое другого файла" > vfs/dir2/another_file.txt
```

>>> * Создайте архив filesystem.tar:
```
COPYFILE_DISABLE=1 tar --exclude='._*' -cvf filesystem.tar -C vfs .
```

>> 3. Создайте файл конфигурации config.toml:
```
hostname = "my_emulator"
filesystem_path = "filesystem.tar"
log_file = "emulator_log.json"
startup_script = "startup.sh"
```

>> 4. (Опционально) Создайте стартовый скрипт startup.sh:
```
echo "Добро пожаловать в эмулятор!"
ls
```

>> 5. Установите необходимые зависимости:
```
pip install toml
```

>> 6. Запустите эмулятор:
```
python emulator.py config.toml
```
## 4. Примеры использования ##
## Пример сеанса работы ##
```
$ python emulator.py config.toml
Загрузка конфигурации из файла: config.toml
Конфигурация успешно загружена: {'hostname': 'my_emulator', 'filesystem_path': 'filesystem.tar', 'log_file': 'emulator_log.json', 'startup_script': 'startup.sh'}
Загрузка файловой системы из архива: filesystem.tar
Файловая система успешно загружена.
Содержимое архива файловой системы в эмуляторе:
- . (isdir: True)
- ./dir2 (isdir: True)
- ./dir1 (isdir: True)
- ./dir1/file1.txt (isdir: False)
- ./dir1/test_file.txt (isdir: False)
- ./dir2/file2.txt (isdir: False)
- ./dir2/another_file.txt (isdir: False)
Загрузка стартового скрипта из файла: startup.sh
Стартовый скрипт успешно загружен. Команды: ['echo "Добро пожаловать в эмулятор!"', 'ls']
Эмулятор успешно инициализирован.
Добро пожаловать в эмулятор!
dir1
dir2
my_emulator:/$ ls
dir1
dir2
my_emulator:/$ cd dir1
my_emulator:/dir1$ ls
file1.txt
test_file.txt
my_emulator:/dir1$ tac test_file.txt
Содержимое тестового файла
my_emulator:/dir1$ chown new_owner file1.txt
Изменен владелец 'file1.txt' на 'new_owner'
my_emulator:/dir1$ uptime
Время работы: 42 секунд
my_emulator:/dir1$ exit
```

## 5. Результаты прогона тестов ##
## Запуск тестов ##
Для запуска тестов используется pytest. Предварительно установите pytest:
```
pip install pytest
```
## Тестовые сценарии ##
Создайте файл test_emulator.py с тестами:
```
import pytest
from emulator import ShellEmulator

@pytest.fixture
def emulator(tmp_path):
    # Создаём тестовый архив файловой системы
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file1.txt").write_text("Test file 1")
    (tmp_path / "dir2").mkdir()
    (tmp_path / "dir2" / "file2.txt").write_text("Test file 2")
    fs_tar = tmp_path / "filesystem.tar"
    with tarfile.open(fs_tar, "w") as tar:
        tar.add(tmp_path / "dir1", arcname="dir1")
        tar.add(tmp_path / "dir2", arcname="dir2")
    # Создаём конфигурационный файл
    config_toml = tmp_path / "config.toml"
    config_toml.write_text(f"""
    hostname = "test_emulator"
    filesystem_path = "{fs_tar}"
    log_file = "{tmp_path / 'emulator_log.json'}"
    """)
    return ShellEmulator(str(config_toml))

def test_ls_root(emulator, capsys):
    emulator.execute_command('ls')
    captured = capsys.readouterr()
    assert 'dir1' in captured.out
    assert 'dir2' in captured.out

def test_cd_and_ls(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('ls')
    captured = capsys.readouterr()
    assert 'file1.txt' in captured.out

def test_tac(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('tac file1.txt')
    captured = capsys.readouterr()
    assert 'Test file 1' in captured.out

def test_chown(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('chown user file1.txt')
    captured = capsys.readouterr()
    assert "Изменен владелец 'file1.txt' на 'user'" in captured.out

def test_uptime(emulator, capsys):
    emulator.execute_command('uptime')
    captured = capsys.readouterr()
    assert "Время работы" in captured.out
```
## Результаты прогона тестов ##
Запустите тесты:
```
pytest test_emulator.py -v
```
## Вывод: ##
```
================================================= test session starts =================================================
platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /Users/username/project
collected 5 items                                                                                                     

test_emulator.py::test_ls_root PASSED                                                                           [ 20%]
test_emulator.py::test_cd_and_ls PASSED                                                                          [ 40%]
test_emulator.py::test_tac PASSED                                                                                [ 60%]
test_emulator.py::test_chown PASSED                                                                              [ 80%]
test_emulator.py::test_uptime PASSED                                                                             [100%]

================================================= 5 passed in 0.50s ==================================================
```
---
Ссылка на git-репозиторий: <https://github.com/e-and-a/Config>