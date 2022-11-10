import argparse
import os
from typing import List


ALIAS_NAME = 'seisviewer'
ALIAS_COMMAND = 'python3.8 -c "from seisviewer.runner import run; run()"'
BASH_FILE = os.path.join(os.path.expanduser('~'), '.bashrc')


def read_bash_file() -> List[str]:
    if not os.path.exists(BASH_FILE):
        return []

    with open(BASH_FILE) as file_ctx:
        return file_ctx.readlines()


def save_lines_to_bash_file(lines: List[str]):
    with open(BASH_FILE, 'w') as file_ctx:
        for line in lines:
            if line[-1] != '\n':
                line = f'{line}\n'
            file_ctx.write(line)


def is_alias_exists(alias_name: str) -> bool:
    if not os.path.exists(BASH_FILE):
        return False

    for line in read_bash_file():
        if f'alias {alias_name}' in line:
            return True
    return False


def set_alias(alias: str, command: str):
    if not os.path.exists(BASH_FILE):
        return

    if is_alias_exists(alias_name=alias):
        return

    with open(BASH_FILE, 'a') as file_ctx:
        line = f'\nalias {alias}=\'{command}\'\n'
        file_ctx.write(line)


def remove_alias(alias: str):
    if not os.path.exists(BASH_FILE):
        return

    lines = read_bash_file()
    print(len(lines))
    for i in range(len(lines)):
        if f'alias {alias}=' in lines[i]:
            lines.pop(i)
            break
    save_lines_to_bash_file(lines=lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Utility for alias and variables configuration'
    )
    parser.add_argument('--install', action='store_true',
                        help='Install alias and variables')
    parser.add_argument('--remove', action='store_true',
                        help='Remove alias and variables')

    args = parser.parse_args()
    if args.install:
        set_alias(alias=ALIAS_NAME, command=ALIAS_COMMAND)

    if args.remove:
        remove_alias(alias=ALIAS_NAME)
