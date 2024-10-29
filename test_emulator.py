import io
import pytest
import os
import tarfile
import json
import toml
from emulator import ShellEmulator

@pytest.fixture
def emulator(tmp_path):
    # Создаем временный config.toml
    config = {
        'hostname': 'test_emulator',
        'filesystem_path': str(tmp_path / 'filesystem.tar'),
        'log_file': str(tmp_path / 'emulator_log.json'),
        'startup_script': str(tmp_path / 'startup.sh'),
    }

    # Сохраняем config.toml
    config_path = tmp_path / 'config.toml'
    with open(config_path, 'w') as f:
        toml.dump(config, f)

    # Создаем виртуальную файловую систему
    with tarfile.open(config['filesystem_path'], 'w') as tar:
        # Создаем директорию home/
        dir_info = tarfile.TarInfo('home/')
        dir_info.type = tarfile.DIRTYPE
        tar.addfile(dir_info)

        # Создаем директорию home/user/
        dir_info = tarfile.TarInfo('home/user/')
        dir_info.type = tarfile.DIRTYPE
        tar.addfile(dir_info)

        # Создаем файл home/user/test.txt
        file_info = tarfile.TarInfo('home/user/test.txt')
        file_content = b'Hello, world!'
        file_info.size = len(file_content)
        tar.addfile(file_info, fileobj=io.BytesIO(file_content))

    # **Добавляем отладочный вывод содержимого архива файловой системы**
    print("Содержимое архива файловой системы:")
    with tarfile.open(config['filesystem_path'], 'r') as tar:
        for member in tar.getmembers():
            print(f"- {member.name} (type: {'dir' if member.isdir() else 'file'})")

    # Создаем пустой startup.sh
    with open(config['startup_script'], 'w') as f:
        f.write('')

    return ShellEmulator(str(config_path))

def test_ls_root(emulator, capsys):
    emulator.execute_command('ls')
    captured = capsys.readouterr()
    assert 'home' in captured.out

def test_cd_and_ls(emulator, capsys):
    emulator.execute_command('cd home/user')
    emulator.execute_command('ls')
    captured = capsys.readouterr()
    assert 'test.txt' in captured.out

def test_tac(emulator, capsys):
    emulator.execute_command('tac home/user/test.txt')
    captured = capsys.readouterr()
    assert 'Hello, world!' in captured.out

def test_chown(emulator, capsys):
    emulator.execute_command('chown new_owner home/user/test.txt')
    captured = capsys.readouterr()
    assert 'Изменен владелец' in captured.out

def test_uptime(emulator, capsys):
    emulator.execute_command('uptime')
    captured = capsys.readouterr()
    assert 'Время работы' in captured.out
