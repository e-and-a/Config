import pytest
import tarfile
from emulator import ShellEmulator
import os
import posixpath

@pytest.fixture
def emulator(tmp_path):
    # Create test filesystem
    (tmp_path / "vfs" / "dir1").mkdir(parents=True)
    (tmp_path / "vfs" / "dir1" / "file1.txt").write_text("Test file 1")
    (tmp_path / "vfs" / "dir2").mkdir()
    (tmp_path / "vfs" / "dir2" / "file2.txt").write_text("Test file 2")
    fs_tar = tmp_path / "filesystem.tar"
    with tarfile.open(fs_tar, "w") as tar:
        tar.add((tmp_path / "vfs" / "dir1").as_posix(), arcname="dir1")
        tar.add((tmp_path / "vfs" / "dir2").as_posix(), arcname="dir2")
    # Create config file
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
    assert 'alice alice' in captured.out  # Owner changed to alice

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
