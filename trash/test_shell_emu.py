import pytest
import os
import shutil
from trash.shell_emu import ShellEmulator

@pytest.fixture(scope='module')
def setup_environment():
    # Создаем конфигурационный файл для тестов
    config_path = "test_config.toml"
    with open(config_path, 'w') as f:
        f.write("""
hostname = "test-computer"
vfs_path = "test_vfs.tar"
log_file = "test_session_log.json"
start_script = "test_startup_script.sh"
""")
    # Создаем тестовый архив виртуальной ФС
    os.makedirs('test_vfs_root/dir1', exist_ok=True)
    with open('test_vfs_root/dir1/test_file.txt', 'w') as f:
        f.write("Test content\nSecond line")
    os.makedirs('test_vfs_root/dir2', exist_ok=True)
    with open('test_vfs_root/dir2/another_file.txt', 'w') as f:
        f.write("Another file content")
    os.system('tar -cvf test_vfs.tar -C test_vfs_root .')

    yield config_path

    # Очистка после тестов
    os.remove(config_path)
    os.remove('test_vfs.tar')
    os.remove('test_session_log.json')
    if os.path.exists('vfs'):
        shutil.rmtree('vfs')
    shutil.rmtree('test_vfs_root')

@pytest.fixture
def shell(setup_environment):
    return ShellEmulator(setup_environment)

def test_ls(shell, capsys):
    shell.ls()
    captured = capsys.readouterr()
    assert 'dir1' in captured.out
    assert 'dir2' in captured.out

def test_ls_in_directory(shell, capsys):
    shell.cd('dir1')
    shell.ls()
    captured = capsys.readouterr()
    assert 'test_file.txt' in captured.out

def test_cd(shell):
    shell.cd('dir1')
    assert shell.current_dir == '/dir1'

def test_cd_nonexistent(shell, capsys):
    shell.cd('nonexistent_dir')
    captured = capsys.readouterr()
    assert "cd: no such file or directory: nonexistent_dir" in captured.out

def test_tac(shell, capsys):
    shell.cd('dir1')
    shell.tac('test_file.txt')
    captured = capsys.readouterr()
    assert "Second line" in captured.out
    assert "Test content" in captured.out

def test_tac_nonexistent_file(shell, capsys):
    shell.tac('nonexistent.txt')
    captured = capsys.readouterr()
    assert "tac: cannot open nonexistent.txt: No such file" in captured.out

def test_chown(shell, capsys):
    shell.cd('dir1')
    shell.chown('test_file.txt', 'new_owner')
    captured = capsys.readouterr()
    assert "Changed owner of test_file.txt to new_owner" in captured.out

def test_chown_nonexistent_file(shell, capsys):
    shell.chown('nonexistent.txt', 'new_owner')
    captured = capsys.readouterr()
    assert "chown: cannot access 'nonexistent.txt': No such file or directory" in captured.out

def test_uptime(shell, capsys):
    shell.uptime()
    captured = capsys.readouterr()
    assert "Uptime:" in captured.out

def test_exit(shell):
    with pytest.raises(SystemExit):
        shell.run_command('exit')

def test_unknown_command(shell, capsys):
    shell.run_command('unknowncmd')
    captured = capsys.readouterr()
    assert "unknowncmd: command not found" in captured.out

def test_start_script_execution(setup_environment, capsys):
    # Создаем стартовый скрипт
    with open('test_startup_script.sh', 'w') as f:
        f.write("""
ls
cd dir1
ls
""")
    shell = ShellEmulator(setup_environment)
    captured = capsys.readouterr()
    assert 'dir1' in captured.out
    assert 'dir2' in captured.out
    assert 'test_file.txt' in captured.out
    os.remove('test_startup_script.sh')

def test_log_file_creation(shell):
    shell.run_command('ls')
    shell.save_log()
    assert os.path.exists('test_session_log.json')
    with open('test_session_log.json', 'r') as log_file:
        log_content = log_file.read()
        assert '"action": "ls /"' in log_content

