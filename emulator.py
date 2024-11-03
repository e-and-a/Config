import os
import tarfile
import sys
import json
import time
import toml
import posixpath # Используем posixpath для работы с путями в формате POSIX
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
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
            return config
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            sys.exit(1)

    def load_filesystem(self):
        fs_path = self.config.get('filesystem_path', 'filesystem.tar')
        try:
            self.tar = tarfile.open(fs_path, 'r')
            # Инициализация словаря владельцев файлов
            self.file_owners = {}
            # Инициализация владельцев файлов по умолчанию
            for member in self.tar.getmembers():
                path_in_tar = posixpath.normpath(member.name)
                self.file_owners[path_in_tar] = 'root'  # Владелец по умолчанию
        except Exception as e:
            print(f"Ошибка загрузки архива файловой системы: {e}")
            sys.exit(1)

    def load_startup_script(self):
        script_path = self.config.get('startup_script', '')
        if script_path and os.path.exists(script_path):
            with open(script_path, 'r') as f:
                self.startup_commands = [line.strip() for line in f if line.strip()]
        else:
            self.startup_commands = []

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
        show_long = False
        paths = []

        # Разбор аргументов
        for arg in args:
            if arg == '-l':
                show_long = True
            else:
                paths.append(arg)

        # Если путь не указан, используем текущий каталог
        if not paths:
            paths = [self.current_path]

        for path in paths:
            abs_path = self.get_absolute_path(path)
            path_in_tar = abs_path.strip('/')
            path_in_tar = posixpath.normpath(path_in_tar)
            if path_in_tar == '.':
                path_in_tar = ''

            entries = []
            for member in self.tar.getmembers():
                member_path = posixpath.normpath(member.name)
                member_dirname = posixpath.dirname(member_path)
                if member_dirname == path_in_tar:
                    member_basename = posixpath.basename(member_path)
                    if member_basename not in ('.', ''):
                        entries.append((member_basename, member))

            if entries:
                for entry_name, member in sorted(entries):
                    if show_long:
                        # Формирование строки с информацией о файле
                        mode = 'd' if member.isdir() else '-'
                        permissions = 'rwxr-xr-x' if member.isdir() else 'rw-r--r--'
                        owner = self.file_owners.get(posixpath.normpath(member.name), 'root')
                        size = member.size
                        mtime = time.strftime('%b %d %H:%M', time.localtime(member.mtime))
                        print(f"{mode}{permissions} 1 {owner} {owner} {size} {mtime} {entry_name}")
                    else:
                        print(entry_name)
            else:
                print(f"ls: {path}: Нет такого файла или каталога")

    def cmd_cd(self, args):
        if not args:
            print("cd: отсутствует аргумент")
            return
        path = self.get_absolute_path(args[0])
        path_in_tar = path.strip('/')
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
                    print(f"tac: {args[0]}: Это каталог")
                    return
                f = self.tar.extractfile(member)
                if f:
                    try:
                        lines = f.read().decode('utf-8').splitlines()
                        for line in reversed(lines):
                            print(line)
                    except UnicodeDecodeError:
                        print(f"tac: {args[0]}: невозможно декодировать файл")
                    return
                else:
                    print(f"tac: {args[0]}: Нет такого файла или каталога")
                    return
        print(f"tac: {args[0]}: Нет такого файла или каталога")

    def cmd_chown(self, args):
        if len(args) < 2:
            print("chown: отсутствует операнд")
            return
        owner = args[0]
        path = self.get_absolute_path(args[1])
        path_in_tar = path.strip('/')
        path_in_tar = posixpath.normpath(path_in_tar)
        found = False
        for member in self.tar.getmembers():
            member_path = posixpath.normpath(member.name)
            if member_path == path_in_tar:
                self.file_owners[member_path] = owner
                print(f"Изменен владелец '{args[1]}' на '{owner}'")
                found = True
                break
        if not found:
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
            print(f"{command}: команда не найдена")

    def run(self):
        # Выполнение команд из стартового скрипта
        for cmd in self.startup_commands:
            self.execute_command(cmd)

        # Основной цикл
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
    emulator.run()
