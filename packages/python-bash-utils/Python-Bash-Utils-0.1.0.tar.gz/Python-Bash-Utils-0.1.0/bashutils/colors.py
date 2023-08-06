#!/usr/local/bin/python
# coding: utf-8

# -----------------------------------------------------------------------------

COLOR_CODES = {
    'none': '\033[39m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'grey': '\033[37m',
}

COLOR_RESET = '\033[0m'

# -----------------------------------------------------------------------------

def get_color(color):
    key = color.lower()
    if not key in COLOR_CODES.keys():
        key = "none"

    return COLOR_CODES[key]


def color_text(text, color="none"):
    color = get_color(color)
    return color + text + COLOR_RESET

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print color_text('red', 'RED')
    print color_text('green', 'GREEN')
    print color_text('yellow', 'YELLOW')
    print color_text('blue', 'BLUE')
    print color_text('magenta', 'MAGENTA')
    print color_text('cyan', 'CYAN')
    print color_text('white', 'WHITE')
    print color_text('grey', 'GREY')

    print color_text('invalid', 'INVALID')
    print color_text('none')
