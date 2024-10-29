import os
import tarfile
import sys
import json
import time
import toml
import posixpath  # Используем posixpath для работы с путями в формате POSIX
from datetime import datetime

class ShellEmulator:
    def __init__(self, config_path):
        self.start_time = time.time()
        self.current_path = '/'
        self.config = self.load_config(config_path)
        self.load_filesystem()
        self.load_startup_script()
        self.log_file = self.config.get('log_file', 'emulator_log.json')
        self.log = []
        self.hostname = self.config.get('hostname', 'emulator')

    def load_config(self, config_path):
        print(f"Загрузка конфигурации из файла: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
            print(f"Конфигурация успешно загружена: {config}")
            return config
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            sys.exit(1)

    def load_filesystem(self):
        fs_path = self.config.get('filesystem_path', 'filesystem.tar')
        print(f"Загрузка файловой системы из архива: {fs_path}")
        try:
            self.tar = tarfile.open(fs_path, 'r')
            print("Файловая система успешно загружена.")
            # Вывод содержимого архива
            print("Содержимое архива файловой системы в эмуляторе:")
            for member in self.tar.getmembers():
                print(f"- {member.name} (isdir: {member.isdir()})")
        except Exception as e:
            print(f"Ошибка загрузки архива файловой системы: {e}")
            sys.exit(1)

    def load_startup_script(self):
        script_path = self.config.get('startup_script', '')
        if script_path and os.path.exists(script_path):
            print(f"Загрузка стартового скрипта из файла: {script_path}")
            with open(script_path, 'r') as f:
                self.startup_commands = [line.strip() for line in f if line.strip()]
            print(f"Стартовый скрипт успешно загружен. Команды: {self.startup_commands}")
        else:
            self.startup_commands = []
            print("Стартовый скрипт не найден или не указан.")

    def log_command(self, command):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': command
        }
        self.log.append(entry)

    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, ensure_ascii=False, indent=4)

    def get_absolute_path(self, path):
        if path.startswith('/'):
            return posixpath.normpath(path)
        else:
            return posixpath.normpath(posixpath.join(self.current_path, path))

    def cmd_ls(self, args):
        path = self.get_absolute_path(args[0]) if args else self.current_path
        path_in_tar = path.strip('/')

        # Нормализация пути
        path_in_tar = posixpath.normpath(path_in_tar)
        if path_in_tar == '.':
            path_in_tar = ''

        entries = set()
        for member in self.tar.getmembers():
            member_path = posixpath.normpath(member.name)
            member_dirname = posixpath.dirname(member_path)
            if member_dirname == path_in_tar:
                member_basename = posixpath.basename(member_path)
                if member_basename not in ('.', ''):
                    entries.add(member_basename)

        if entries:
            for entry in sorted(entries):
                print(entry)
        else:
            print(f"ls: {path}: Нет такого файла или каталога")

    def cmd_cd(self, args):
        if not args:
            print("cd: отсутствует аргумент")
            return
        path = self.get_absolute_path(args[0])
        path_in_tar = path.strip('/')

        # Нормализация пути
        path_in_tar = posixpath.normpath(path_in_tar)
        if path_in_tar == '.':
            path_in_tar = ''

        for member in self.tar.getmembers():
            member_path = posixpath.normpath(member.name).rstrip('/')
            if member_path == path_in_tar and member.isdir():
                self.current_path = path
                return
        print(f"cd: нет такого файла или каталога: {args[0]}")

    def cmd_tac(self, args):
        if not args:
            print("tac: отсутствует аргумент")
            return

        path = self.get_absolute_path(args[0])
        path_in_tar = path.strip('/')
        path_in_tar = posixpath.normpath(path_in_tar)

        for member in self.tar.getmembers():
            member_path = posixpath.normpath(member.name)
            if member_path == path_in_tar:
                if member.isdir():
                    print(f"tac: невозможно открыть '{args[0]}' для чтения: Это каталог")
                    return
                f = self.tar.extractfile(member)
                if f:
                    lines = f.read().decode('utf-8').splitlines()
                    for line in reversed(lines):
                        print(line)
                    return
                else:
                    print(f"tac: невозможно открыть '{args[0]}' для чтения: Нет такого файла или каталога")
                    return

        print(f"tac: невозможно открыть '{args[0]}' для чтения: Нет такого файла или каталога")

    def cmd_chown(self, args):
        if len(args) < 2:
            print("chown: отсутствует операнд")
            return
        owner = args[0]
        path = self.get_absolute_path(args[1])
        path_in_tar = path.strip('/')
        path_in_tar = posixpath.normpath(path_in_tar)
        for member in self.tar.getmembers():
            member_path = posixpath.normpath(member.name)
            if member_path == path_in_tar:
                print(f"Изменен владелец '{args[1]}' на '{owner}'")
                # Здесь можно добавить логику изменения владельца в метаданных, если требуется
                return
        print(f"chown: невозможно изменить владельца '{args[1]}': Нет такого файла или каталога")

    def cmd_uptime(self):
        elapsed_time = int(time.time() - self.start_time)
        print(f"Время работы: {elapsed_time} секунд")

    def cmd_exit(self):
        self.save_log()
        sys.exit(0)

    def execute_command(self, command_line):
        command_line = command_line.strip()
        if not command_line:
            return
        parts = command_line.split()
        command = parts[0]
        args = parts[1:]

        # Логирование команды
        self.log_command(command_line)

        if command == 'ls':
            self.cmd_ls(args)
        elif command == 'cd':
            self.cmd_cd(args)
        elif command == 'tac':
            self.cmd_tac(args)
        elif command == 'chown':
            self.cmd_chown(args)
        elif command == 'uptime':
            self.cmd_uptime()
        elif command == 'exit':
            self.cmd_exit()
        else:
            print(f"Команда не найдена: {command}")

    def run(self):
        # Выполнение команд из стартового скрипта
        for cmd in self.startup_commands:
            self.execute_command(cmd)

        # Основной цикл эмулятора
        while True:
            try:
                prompt = f"{self.hostname}:{self.current_path}$ "
                command_line = input(prompt)
                self.execute_command(command_line)
            except EOFError:
                self.cmd_exit()
            except KeyboardInterrupt:
                print()
                continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python emulator.py config.toml")
        sys.exit(1)
    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    print("Эмулятор успешно инициализирован.")
    emulator.run()
