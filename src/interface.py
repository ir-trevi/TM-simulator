import os

class Interface:

    def __init__(self, state: str, input_tape: str, steps: int, view_code: list[tuple[bool, str]], view_tape: str, global_var: dict, 
                 writing: bool = False, status_bar: str = "Simulating... (Press \"space\" to pause)") -> None:
        r"""
        Creates a new instance of ``Interface``.

        ``state`` is the current state of the machine, ``input_tape`` represents the initial tape input for the user,
        ``steps`` is number of steps executed, ``view_code`` is a list of tuples to display taken as they are from the file,
        ``global_var`` keeps all the global variables, ``writing`` tells if the machine is writing to a cell on the tape and
        ``status_bar`` is the message displayed in the bottom part of the window

        When the interface is initiated it runs ``show()``
        """

        self.state = state
        self.input_tape = input_tape
        self.steps = steps
        self.view_code = view_code
        self.view_tape = view_tape
        self.writing = writing
        self.global_var = global_var
        self.status_bar = status_bar
        self.show()

    def show(self) -> None:
        r"""
        Prints the interface based on the current values of the machine.
        It buffers the whole string representing the interface and prints it all at once at the end.
        Previous interfaces printed are not deleted to avoid flashing images due to the high refresh frequency.
        """

        def show_code(index: int, arrow: bool) -> str:
            return (f" {'->' if arrow else '  '} {'!' if self.view_code[index - 3][0] else ' '}"
                    f" {self.view_code[index - 3][1]}").ljust(self.global_var["code_size"] - 1)[:self.global_var["code_size"] - 1] + "║\n"
        length, height = tuple(os.get_terminal_size())
        if self.global_var["code_size"] + self.global_var["tape_size"] * (2 if self.global_var["slim_tape"] else 4) + 10 > length or height < 20 or length < 120:
            os.system("cls" if os.name == "nt" else "clear")
            print("The terminal window size was changed while the simulator was running and the new size is not supported")
            exit()

        c = (height - 8) // 2
        buffer_string = ''
        no_code = self.global_var["code_size"] == 0
        for i in range(height):
            if i == 0:
                buffer_string += f"╔{'═' * (length - 2)}╗"
            elif i == 1:
                buffer_string += f"║{'Turing Machine Simulator'.center(length)[1:-1]}║"
            elif i == 2:
                buffer_string += f"╠{'═' * (length - self.global_var['code_size'] - 2)}╤{'═' * (self.global_var['code_size'] - 1)}╣" if not no_code \
                            else f"╠{'═' * (length - 2)}╣"
            elif i == c - 6:
                upper_part = f"┌{'─' * (self.global_var['tape_size'] - 2)}┐"
                buffer_string += (f"║{upper_part.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{upper_part.center(length - 2)}║"
            elif i == c - 5:
                text = f"│{self.state.center(self.global_var['tape_size'] - 2)}│"
                buffer_string += (f"║{text.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{text.center(length - 2)}║"
            elif i == c - 4:
                lower_part = f"└{'─' * (self.global_var['tape_size'] - 2)}┘"
                buffer_string += (f"║{lower_part.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{lower_part.center(length - 2)}║"
            elif i == c + 2:
                buffer_string += (f"║{'│'.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{'│'.center(length - 2)}║"
            elif i == c + 3:
                arrow_tip = '*' if self.writing else 'V'
                buffer_string += (f"║{arrow_tip.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, True)) if not no_code \
                            else f"║{arrow_tip.center(length - 2)}║"
            elif i == c + 4:
                upper_tape = f"─{('┬─' if self.global_var['slim_tape'] else '─┬──') * (self.global_var['tape_size'] + 1)}"
                buffer_string += (f"║{upper_tape.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{upper_tape.center(length - 2)}║"
            elif i == c + 5:
                tape_content = f"  │ {' │ '.join(self.view_tape.upper())} │  "
                tape_content = f" {tape_content.replace(' │ ', '│')} " if self.global_var['slim_tape'] else tape_content
                buffer_string += (f"║{tape_content.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{tape_content.center(length - 2)}║"
            elif i == c + 6:
                lower_tape = f"─{('┴─' if self.global_var['slim_tape'] else '─┴──') * (self.global_var['tape_size'] + 1)}"
                buffer_string += (f"║{lower_tape.center(length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{lower_tape.center(length - 2)}║"
            elif i == height - 5:
                buffer_string += (f"╟{'─' * (length - self.global_var['code_size'] - 2)}┤" + show_code(i, False)) if not no_code \
                            else f"╟{'─' * (length - 2)}╢"
            elif i == height - 4:
                input_string = self.input_tape.upper()
                buffer_string += (f"║  Input: {input_string.ljust(length - self.global_var['code_size'] - 10)}"[:length - self.global_var["code_size"] - 1] +
                                  '│' + show_code(i, False)) if not no_code \
                            else f"║  Input: {input_string.ljust(length - 1)}"[:length - 1] + '║'
            elif i == height - 3:
                buffer_string += f"╠{'═' * (length - self.global_var['code_size'] - 2)}╧{'═' * (self.global_var['code_size'] - 1)}╣" if not no_code \
                            else f"╠{'═' * (length - 2)}╣"
            elif i == height - 2:
                text = f"  Simulation speed: {self.global_var['speed']}   Steps counter: {self.steps}    " + \
                       ("Press \"q\" at any moment to stop the simulation... " if not self.status_bar else
                        self.status_bar)
                buffer_string += f"║{text.ljust(length - 2)}║"
            elif i == height - 1:
                buffer_string += f"╚{'═' * (length - 2)}╝"
            else:
                buffer_string += (f"║{' ' * (length - self.global_var['code_size'] - 2)}│" + show_code(i, False)) if not no_code \
                            else f"║{' ' * (length - 2)}║"
        print(buffer_string, end='', flush=True)
