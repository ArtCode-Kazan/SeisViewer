import os


ALIAS_NAME = 'seisviewer'
ALIAS_COMMAND = 'python3.8 -c "from seisviewer.runner import run; run()"'


def is_alias_exists(bash_file_path: str):
    if not os.path.exists(bash_file_path):
        return False

    with open(bash_file_path) as file_ctx:
        for line in file_ctx:
            if f'alias {ALIAS_NAME}' in line:
                return True
    return False


def set_alias(bash_file_path: str):
    if not os.path.exists(bash_file_path):
        return

    with open(bash_file_path, 'a') as file_ctx:
        line = f'alias {ALIAS_NAME}=\'{ALIAS_COMMAND}\''
        file_ctx.write(line)


if __name__ == '__main__':
    bash_file = os.path.join(os.path.expanduser('~'), '.bashrc')
    if not is_alias_exists(bash_file_path=bash_file):
        set_alias(bash_file_path=bash_file)
