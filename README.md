# Shell Emulator


## 1. Общее описание ##

 Shell Emulator — это консольное приложение на Python, эмулирующее работу простой командной оболочки. Эмулятор позволяет пользователю взаимодействовать с виртуальной файловой системой, хранящейся в архиве tar. Он поддерживает базовые команды для навигации и управления файлами, такие как ls, cd, tac, chown, uptime и exit.

Эмулятор читает конфигурацию из файла config.toml, который задаёт параметры работы приложения, включая путь к файловой системе, лог-файлу и стартовому скрипту. Приложение также сохраняет историю введённых команд в лог-файл в формате JSON.


## 2. Описание функций и настроек ##

## Основные функции ##

* Загрузка файловой системы из архива tar: Эмулятор читает файловую систему из указанного архива и позволяет просматривать и навигировать по ней.

* Поддержка команд оболочки:
> * ls [options] [path]: отображает содержимое указанного каталога.
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

> ls [options] [path]
Отображает содержимое указанного каталога. Если путь не указан, отображает содержимое текущего каталога.
> Опции:
-l: выводит подробную информацию о файлах в формате длинного списка, включая права доступа, владельца, размер и дату изменения.

** Пример: **
```
my_emulator:/dir1$ ls
file1.txt
test_file.txt

my_emulator:/dir1$ ls -l
-rw-r--r-- 1 root      root      34 Oct 29 08:23 file1.txt
-rw-r--r-- 1 root      root      51 Oct 29 08:23 test_file.txt

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
Изменяет владельца указанного файла или каталога на указанного пользователя. Изменения сохраняются в эмуляторе и отображаются при выводе списка файлов с помощью ls -l.

** Пример: **
```
my_emulator:/dir1$ chown new_owner file1.txt
Изменен владелец 'file1.txt' на 'new_owner'

my_emulator:/dir1$ ls -l
-rw-r--r-- 1 new_owner new_owner 34 Oct 29 08:23 file1.txt
-rw-r--r-- 1 root      root      51 Oct 29 08:23 test_file.txt

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
# Стартовый скрипт для эмулятора
cd dir1
ls -l
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
dir1
dir2
my_emulator:/dir1$ ls -l
-rw-r--r-- 1 root root 34 Oct 29 08:23 file1.txt
-rw-r--r-- 1 root root 51 Oct 29 08:23 test_file.txt
my_emulator:/dir1$ chown new_owner file1.txt
Изменен владелец 'file1.txt' на 'new_owner'
my_emulator:/dir1$ ls -l
-rw-r--r-- 1 new_owner new_owner 34 Oct 29 08:23 file1.txt
-rw-r--r-- 1 root      root      51 Oct 29 08:23 test_file.txt
my_emulator:/dir1$ tac test_file.txt
Третья строка файла
Вторая строка файла
Первая строка файла
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
import tarfile
from emulator import ShellEmulator
import os
import posixpath

@pytest.fixture
def emulator(tmp_path):
    # Создаём тестовый архив файловой системы
    (tmp_path / "vfs" / "dir1").mkdir(parents=True)
    (tmp_path / "vfs" / "dir1" / "file1.txt").write_text("Test file 1")
    (tmp_path / "vfs" / "dir2").mkdir()
    (tmp_path / "vfs" / "dir2" / "file2.txt").write_text("Test file 2")
    fs_tar = tmp_path / "filesystem.tar"
    with tarfile.open(fs_tar, "w") as tar:
        tar.add((tmp_path / "vfs" / "dir1").as_posix(), arcname="dir1")
        tar.add((tmp_path / "vfs" / "dir2").as_posix(), arcname="dir2")
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

def test_ls_long_format(emulator, capsys):
    emulator.execute_command('ls -l')
    captured = capsys.readouterr()
    assert 'drwxr-xr-x 1 root root' in captured.out
    assert 'dir1' in captured.out
    assert 'dir2' in captured.out

def test_chown_and_ls(emulator, capsys):
    emulator.execute_command('chown alice dir1')
    emulator.execute_command('ls -l')
    captured = capsys.readouterr()
    assert 'dir1' in captured.out
    assert 'alice alice' in captured.out  # Владелец изменён на alice

def test_cd_and_ls(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('ls')
    captured = capsys.readouterr()
    assert 'file1.txt' in captured.out

def test_chown_file(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('chown bob file1.txt')
    emulator.execute_command('ls -l')
    captured = capsys.readouterr()
    assert 'file1.txt' in captured.out
    assert 'bob bob' in captured.out

def test_tac(emulator, capsys):
    emulator.execute_command('cd dir1')
    emulator.execute_command('tac file1.txt')
    captured = capsys.readouterr()
    assert 'Test file 1' in captured.out

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
platform darwin -- Python 3.x.x, pytest-x.x.x, py-x.x.x, pluggy-x.x.x
cachedir: .pytest_cache
rootdir: /path/to/project
collected 7 items                                                                                                    

test_emulator.py::test_ls_root PASSED                                                                          [ 14%]
test_emulator.py::test_ls_long_format PASSED                                                                   [ 28%]
test_emulator.py::test_chown_and_ls PASSED                                                                     [ 42%]
test_emulator.py::test_cd_and_ls PASSED                                                                        [ 57%]
test_emulator.py::test_chown_file PASSED                                                                       [ 71%]
test_emulator.py::test_tac PASSED                                                                              [ 85%]
test_emulator.py::test_uptime PASSED                                                                           [100%]

================================================= 7 passed in 0.60s ==================================================
```
---
Ссылка на git-репозиторий: <https://github.com/e-and-a/Config>