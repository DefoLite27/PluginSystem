from colorama import Fore, Style
import builtins

def info(msg):
    if builtins.settings['debug']:
        print(Fore.BLUE + msg + Style.RESET_ALL)

def warn(msg):
    if builtins.settings['debug']:
        print(Fore.YELLOW + msg + Style.RESET_ALL)

def success(msg):
    if builtins.settings['debug']:
        print(Fore.GREEN + msg + Style.RESET_ALL)

def error(msg):
    if builtins.settings['debug']:
        print(Fore.RED + msg + Style.RESET_ALL)