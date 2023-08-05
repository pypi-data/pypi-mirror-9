"""Console based paging and menu module

Author: Mike Bond <mikeb@hitachi-id.com>
Python version: Python 3.x

Requires colorama, ansicolors, and readline.

"""
import os
import sys
import re
import __main__ as main
import readline
from colorama import init, Style
import colors


class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        char = self.impl()
        if char == '\x03':
            raise KeyboardInterrupt
        elif char == '\x04':
            raise EOFError
        return char


# noinspection PyUnresolvedReferences
class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


class _TermSize():
    """Terminal size object for non-interactive scripts"""

    def __init__(self):
        self.lines = 25
        self.columns = 80


class Menu():
    """The class for console based menu paging."""

    def __init__(self, title, default, choices, multicolumn=True):
        """Initialize the menu for console paging.

        :param str title: An optional menu title
        :param default: An optional key for the default option
        :param dict choices: A dictionary of choices
        :param bool multicolumn: Optional multicolumn output (default = True)

        """

        self.title = title
        self.default = default
        self.choices = choices
        self.multicolumn = multicolumn
        self.menu_choices = sorted(list(self.choices.keys()))

        # default configuration
        self.prompt = 'Your choice => '

        # determine terminal size
        try:
            self.term_size = os.get_terminal_size()
            self.column_width = self.term_size.columns
        except OSError:
            self.term_size = _TermSize()
            self.column_width = self.term_size.columns
        except BaseException as base_error:
            print('An unknown error occurred: {}'.format(base_error))
            sys.exit(1)

        # determine the history filename
        if hasattr(main, '__file__'):
            self.hist_filename = '.history_{}'.format(
                os.path.basename(main.__file__)
            )

        # find the longest choice
        if self.multicolumn:
            self._find_longest()

        # calculate number of columns to fit
        self.columns = 1
        if self.multicolumn:
            self.columns = int(self.term_size.columns / self.column_width)
            self.columns = self.columns == 0 and 1 or self.columns

        # initialize colorama
        init(autoreset=True)

        # initialize readline support
        if hasattr(self, 'hist_filename') and os.path.exists(self.hist_filename):
            readline.read_history_file(self.hist_filename)
        readline.parse_and_bind('tab: complete')

        # TODO: move default styling to code for displaying choices
        # initialize the default choice
        # if self.default and self.choices.get(self.default):
        #     self._style_default()

    @staticmethod
    def _sanitize(description):
        """Sanitize the given description, removing ansi codes

        :param str description: The choice description

        """

        return re.sub('\033\[((?:\d|;)*)([a-zA-Z])', '',
                      description)

    def _style_default(self):
        """Update the style of the default option"""

        if not self.default or self.default not in self.choices:
            return

        # initialize the default choice
        self.choices[self.default] = '{}{}'.format(
            colors.white(self.choices[self.default], style='bold+underline'),
            Style.RESET_ALL
        )

    def _find_longest(self):
        """Find the longest choice by string length"""

        longest = 0
        for choice, value in self.choices.items():
            if len(str(value)) > longest:
                longest = len(str(value))
        self.column_width = longest + 9

    def pager(self):
        """Display the list of choices for paging only, no choice prompt."""

        # calculate output space without title and paging line
        title_lines = self.title is None and 0 or 1
        max_lines = self.term_size.lines - title_lines
        if len(self.menu_choices) > max_lines:
            max_lines -= 1

        page_sizes = []
        index = 0  # index into self.menu_choices
        while True:
            console_line = 0        # current console output line
            page_start = index + 1  # current page starting index

            # display line separator and title
            sys.stdout.write('=' * self.term_size.columns)
            if self.title:
                print(self.title)

            while console_line < max_lines and index < len(self.menu_choices):
                output = ''

                # build the output string for multiple columns
                for column in range(0, self.columns):
                    # check if index choice exists
                    if index >= len(self.menu_choices):
                        break

                    # retrieve choice output value
                    description = self.choices.get(self.menu_choices[index])
                    description = description.strip()

                    # generate the output choice padded to column width
                    if self.multicolumn:
                        width = self.column_width - len(self._sanitize(description))
                        output += '{}{}'.format(description, ' ' * width)
                    else:
                        output = description

                    # increment choices index
                    index += 1

                # calculate console lines with newline characters in output
                console_line += 1 + output.count(os.linesep)

                # back up one option, if needed
                if console_line > max_lines:
                    console_line -= 1 - output.count(os.linesep)
                    index -= 1
                else:
                    print(output)

            # track page size displayed for previous page
            page_sizes.append(index - (page_start - 1))

            sys.stdout.write('<q/Q>Quit, {}{}-{} of {}:'.format(
                page_start > 1 and '<->Prev, ' or '',
                page_start,
                index,
                len(self.menu_choices))
            )
            sys.stdout.flush()

            # wait for key press
            while True:
                reply = str(getch())

                # handle key press
                if reply in ['Q', 'q']:
                    # clear end of line before exit
                    sys.stdout.write(os.linesep)
                    sys.exit(0)
                # go back one page
                elif reply == '-':
                    if page_start == 1:
                        continue

                    # must be popped twice for previous page
                    page_sizes.pop()
                    page_delta = page_sizes.pop()
                    index = (page_start - 1) - page_delta
                    # make sure we don't go past the first index
                    if index < 0:
                        index = 0

                    # clear end of line for next output
                    sys.stdout.write(os.linesep)
                    break
                else:
                    if index >= len(self.menu_choices):
                        continue

                    # clear end of line for next output
                    sys.stdout.write(os.linesep)
                    break

    def chooser(self):
        """Display the list of choices and choice prompt."""

        # calculate output space without title and paging line
        title_lines = self.title is None and 0 or 1
        max_lines = self.term_size.lines - title_lines
        if len(self.menu_choices) > max_lines:
            max_lines -= 2

        # remove line for displaying default selection
        if self.default and self.default in self.choices:
            max_lines -= 1

        page_sizes = []
        index = 0  # index into self.menu_choices
        while True:
            console_line = 0        # current console output line
            page_start = index + 1  # current page starting index

            # display line separator and title
            sys.stdout.write('=' * self.term_size.columns)
            if self.title:
                print(self.title)

            while console_line < max_lines and index < len(self.menu_choices):
                output = ''

                # build the output string for multiple columns
                for column in range(0, self.columns):
                    # check if index choice exists
                    if index >= len(self.menu_choices):
                        break

                    # retrieve choice output value
                    description = self.choices.get(self.menu_choices[index])
                    description = description.strip()

                    # generate the output choice padded to column width
                    number_padding = len(str(len(self.menu_choices)))
                    value = '{}. {}'.format(
                        str(index - page_start + 2).rjust(number_padding),
                        description,
                    )
                    if self.multicolumn:
                        width = self.column_width - len(self._sanitize(value))
                        output += '{}{}'.format(
                            value,
                            ' ' * width
                        )
                    else:
                        output = value

                    # increment choices index
                    index += 1

                # calculate console lines with newline characters in output
                console_line += 1 + output.count(os.linesep)

                # back up one option, if needed
                if console_line > max_lines:
                    console_line -= 1 - output.count(os.linesep)
                    index -= 1
                else:
                    print(output)

            # track page size displayed for previous page
            page_sizes.append(index - (page_start - 1))

            print('----- <space>Next, <->Prev, <q>Quit, <Q>Quit program -----')

            # output default choice
            if self.default and self.default in self.choices:
                print('Default: {}'.format(self.choices.get(self.default)))

            while True:
                reply = input('({}-{} of {}) {}'.format(
                    page_start,
                    index,
                    len(self.menu_choices),
                    self.prompt
                ))

                # quit the entire program
                if reply == 'Q':
                    print('Quitting program')
                    sys.exit(0)
                # quit the current selection (or program)
                elif reply == 'q':
                    return None
                # next page
                elif reply == ' ':
                    if index >= len(self.menu_choices):
                        print('Already at the bottom...')
                        continue
                    break
                # previous page
                elif reply == '-':
                    if page_start == 1:
                        print('Already at the top...')
                        continue

                    # must be popped twice for previous page
                    page_sizes.pop()
                    page_delta = page_sizes.pop()
                    index = (page_start - 1) - page_delta

                    # make sure we don't go past the first index
                    if index < 0:
                        index = 0

                    break
                # return default option
                elif reply == '':
                    if self.default and self.default in self.choices:
                        return self.default
                    continue
                else:
                    # check for numerical choice
                    try:
                        int_choice = int(reply)
                        if int_choice > page_sizes[-1]:
                            print('Option not valid, choose again...')
                            continue
                        if int_choice <= len(self.menu_choices):
                            return self.menu_choices[page_start + int_choice - 2]
                    # otherwise, filter choices and show filtered Menu
                    except ValueError:
                        new_choices = {new_choice: self.choices.get(new_choice)
                                       for new_choice in self.menu_choices
                                       if reply.lower() in
                                           self.choices.get(new_choice).lower()}

                        if len(new_choices) == 0:
                            print('No menu items match: {}'.format(reply))
                            input('Press <Enter> to continue...')
                            continue

                        new_menu = Menu(
                            self.title, self.default, new_choices,
                            multicolumn=self.multicolumn
                        )
                        new_result = new_menu.chooser()
                        if new_result:
                            return new_result

                        # restart previous menu
                        page_sizes.clear()
                        index = 0
                        break

if __name__ == '__main__':

    testing_data = {i: 'Testing {}'.format(i) for i in range(1, 1001)}
    menu = Menu('Make a choice:', 1, testing_data)
    result = menu.chooser()
    print('Choice: {} = {}'.format(result, testing_data.get(result)))

    # multiple page output without choosing
    menu.pager()
