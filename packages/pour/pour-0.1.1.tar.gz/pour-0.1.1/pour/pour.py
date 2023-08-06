import os
import shutil
import click


@click.command()
@click.option('-n', default='app', help='Desired name of app.')
@click.option('-t', is_flag=True, help='Generate test skeleton.')
def generate(n, t):
    filename = n + '.py'
    dirpath = os.path.dirname(os.path.realpath(__file__))
    shutil.copy(os.path.join(dirpath, filename), '.')
    if t:
        shutil.copy(os.path.join(dirpath, 'test.py'), '.')


if __name__ == '__main__':
    generate()
