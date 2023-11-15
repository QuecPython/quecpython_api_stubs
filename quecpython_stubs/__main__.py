import win32api
import win32con
from pathlib import Path


def load():
    # 获取QuecPython的环境变量
    QUECPYTHON_PATH = str(Path(__file__).parent)
    # 打开环境变量键
    key = win32api.RegOpenKeyEx(
        win32con.HKEY_LOCAL_MACHINE,
        'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
        0,
        win32con.KEY_ALL_ACCESS
    )
    # 更新环境变量值
    win32api.RegSetValueEx(key, 'PYTHONPATH', 0, 2, QUECPYTHON_PATH)
    # 关闭键
    win32api.RegCloseKey(key)


if __name__ == '__main__':
    load()
