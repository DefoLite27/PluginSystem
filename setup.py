import subprocess
import sys

def install_packages():
    required_packages = [
        'json5',
    ]
    for package in required_packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

if __name__ == '__main__':
    install_packages()