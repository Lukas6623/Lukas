import os
import sys
import subprocess

def restart():
    """ Перезапуск текущего скрипта """
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    restart()
