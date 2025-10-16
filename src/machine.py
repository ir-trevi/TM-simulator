import os
import time
import keyboard
from tuples import TuringTuple
from interface import Interface

class TuringMachine:

    def __init__(self, input_tape: str, code: list[TuringTuple], breakpoints_list: list[bool], raw_code: list[str],
                 code_map: list[int], pars_errors: list, global_var: dict) -> None:
        r"""
        Creates a new instance of ``TuringMachine`` based on the parsed tuples in ``code``.

        ``input_tape`` is the starting tape, ``breakpoints_list`` represents the indexes of the breakpoints,
        ``raw_code`` is the code as it is in the file, ``code_map`` maps all the expanded tuples back to the original raw_tuple,
        ``pars_errors`` represents all the errors in the parsing process and ``global_var`` keeps all the global variables

        When the machine is initiated it runs ``_check_determinism()``
        """

        self.global_var = global_var
        self.input_tape = input_tape
        self.code = code
        self.raw_code = raw_code
        self.code_map = code_map
        self.breakpoints_list = breakpoints_list
        self.state = "0"
        self.tape_position = 0
        self.tape = list(input_tape)
        self.steps = 0
        self.paused = True
        self.ended = False
        self.silent = False
        self.error = None
        self._prec_index = 0
        self._first_view = True
        self.pars_errors = pars_errors
        self._check_determinism() if not self.silent else None
        if len(self.pars_errors) != 0:
            is_direct = isinstance(self.pars_errors[0][0], list)
            error_line = self.pars_errors[0][0][0] if is_direct else self.pars_errors[0][0]
            if not self.global_var["instant"]:
                error_interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(error_line, not is_direct),
                                            self._get_view_tape(), self.global_var, False, self._get_error_message())
                self.error = error_interface
            else:
                print(self._get_error_message())
                exit()

    def _check_determinism(self) -> None:
        r"""Scans the code to find any non-deterministic combination of tuples, adding any error to ``self.pars_errors``"""
        dictionary = {}
        for element in self.code:
            current_param = (element.current_state, element.current_symbol)
            new_param = (element.new_state, element.new_symbol, element.movement)
            if current_param not in dictionary:
                dictionary.update({current_param: [new_param]})
            else:
                dictionary[current_param].append(new_param)

        for current_param, new_param_list in list(dictionary.items()):
            if len(list(dict.fromkeys(new_param_list))) != 1:
                index_list = []
                for i, element in enumerate(self.code):
                    for new_param in new_param_list:
                        if (element.current_state, element.current_symbol) == current_param and \
                           (element.new_state, element.new_symbol, element.movement) != new_param:
                            index_list.append(i)
                self.pars_errors.append((index_list, 'non_deterministic'))

    def _get_error_message(self) -> str:
        r"""Returns the error message based on the first error occurrence in ``self.pars_errors``"""
        error_code = self.pars_errors[0][1]
        multiple_lines = isinstance(self.pars_errors[0][0], list)
        error_lines = ", ".join(list(dict.fromkeys([str(self.code_map[i]) for i in self.pars_errors[0][0]]))[:5]) if multiple_lines else self.pars_errors[0][0]
        error_message = f'Error at line{"s" if multiple_lines else ""} {error_lines}: '
        match error_code:
            case 'incompatible_dot_limiters':
                error_message += 'the characters limiting the dot notation are not of the same time'
            case 'descending_order':
                error_message += 'the characters limiting the dot notation are in ascending order'
            case 'symbol_dot_limiter':
                error_message += 'the characters limiting the dot notation are symbols'
            case 'missing_class_limiters':
                error_message += 'a bracket enclosing the class is missing'
            case 'empty_class':
                error_message += 'the class is empty'
            case 'multiple_class_types':
                error_message += 'there are different class types in the same rule element'
            case 'multiple_class':
                error_message += 'there are multiple classes in the same rule element'
            case 'empty_rule':
                error_message += 'a rule element is empty'
            case 'unrecognised_movement':
                error_message += 'the movement is not one of the three (\'<\', \'>\', \'-\')'
            case 'different_class_sizes':
                error_message += 'the classes have different sizes'
            case 'multiple_symbols':
                error_message += 'there are multiple characters as the character to read/write'
            case 'incorrect_arguments_amount':
                error_message += 'a rule element is missing'
            case 'opening_char_missing':
                error_message += 'the opening char \'(\' is missing'
            case 'closing_char_missing':
                error_message += 'the closing char \')\' is missing'
            case 'non_deterministic':
                error_message += 'these tuples will lead to non-deterministic behaviour'
            case _:
                error_message += 'an unspecified error occurred'
        return error_message

    def _get_view_code(self, index: int, direct: bool = False) -> list[tuple[bool, str]]:
        r"""Returns the visible part of the code to be displayed"""
        return_list = []
        code_height = tuple(os.get_terminal_size())[1] - 6
        code_index = self.code_map[index] if not direct else index
        for i in range(code_index - code_height // 2 + 1, code_index + code_height // 2 + 2):
            try:
                if i < 0:
                    raise IndexError
                code = self.raw_code[i].replace("!(", "(", 1) if self.raw_code[i].strip()[:2] == "!(" else self.raw_code[i]
                return_list.append((self.breakpoints_list[i], code))
            except IndexError:
                return_list.append((False, ""))
        return return_list

    def _get_view_tape(self) -> str:
        r"""Returns the visible part of the tape to be displayed"""
        return_string = ""
        for i in range(self.tape_position - self.global_var["tape_size"] // 2, self.tape_position + self.global_var["tape_size"] // 2 + 1):
            try:
                if i < 0:
                    raise IndexError
                return_string += self.tape[i]
            except IndexError:
                return_string += " "
        return return_string

    def _remapped_char(self, char: str) -> str:
        r"""Returns the escaped version of ``char`` if ``char`` is a special char"""
        special_view_chars = [' ', '\\', '-', '(', ')', '^', ',', '#', '[', ']', '{', '}']
        special_code_char = ['-', '\\\\', '\\-', '\\(', '\\)', '\\^', '\\,', '\\#', '\\[', '\\]', '\\{', '\\}']
        current_char = char
        if current_char in special_code_char:
            current_char = special_view_chars[special_code_char.index(current_char)]
        return current_char

    def pause(self) -> None:
        r"""Pauses or resumes the simulation"""
        if not self.silent and not self.error and not self.ended:
            self.paused = not self.paused

    def move_right(self) -> None:
        r"""Moves the tape to the right if ``self.ended``, else it steps forward once"""
        if self.silent or self.error:
            return None
        elif self.paused:
            old_speed = self.global_var["speed"]
            self.change_speed(2)
            self.step(stepping=True)
            self.change_speed(old_speed)
        elif self.ended:
            if self.tape_position == len(self.tape) - 1:
                self.tape = self.tape + [" "]
            self.tape_position += 1

    def move_left(self) -> None:
        r"""
        Moves the tape to the left if ``self.ended``, else it steps back once.

        Since stepping backward in a turing machine will lead to non-deterministic results, this functions runs a new instance
        of ``TuringMachine`` up to a step before the main one, then sets the main ``TuringMachine`` variables to the other ones.
        """
        if self.silent or self.error:
            return None
        elif self.paused:
            back_machine = TuringMachine(self.input_tape, self.code, self.breakpoints_list, self.raw_code, self.code_map, self.pars_errors, self.global_var)
            back_machine.silent = True
            while back_machine.steps < self.steps - 1:
                back_machine.step()
            self.state = back_machine.state
            self.tape_position = back_machine.tape_position
            self.tape = back_machine.tape
            self.steps = back_machine.steps
            self._prec_index = back_machine._prec_index
        elif self.ended:
            if self.tape_position == 0:
                self.tape = [" "] + self.tape
                self.tape_position += 1
            self.tape_position -= 1

    def change_speed(self, value: int) -> None:
        r"""Changes the simulation speed to ``value``"""
        if self.paused:
            self.global_var["speed"] = 10 if value == 0 else value

    def terminate(self) -> None:
        r"""Terminates the simulation"""
        keyboard.send("enter")  # used to add \n to the input buffer
        keyboard.send("enter")
        input()  # fetch the buffer up to the first \n
        input()
        os._exit(0)

    def restart(self) -> None:
        r"""Resets all the parameters and restarts the simulation"""
        if self.paused or self.ended:
            time.sleep(0.1)
            self.steps = 0
            self.state = "0"
            self.tape = list(self.input_tape)
            self.tape_position = 0
            self.ended = False
            self.paused = True

    def step(self, stepping: bool = False) -> None:
        r"""
        Steps the machine forward once, updating its status and displaying the changes to the interface (if selected).
        ``stepping`` is used when the machine is manually stepped by the user (``move_right``).
        """
        if self.error:
            self.error.show()
            return None
        if ((self.paused and not stepping) or self.ended) and not self.global_var["instant"] and not self.silent:
            if self.steps == 0:
                status_message = "Press \"space\" to start the simulation"
            elif self.paused:
                status_message = "Simulation paused! (Press \"space\" to resume)"
            else:
                status_message = "Simulation ended! (Press \"q\" to exit)"
            Interface(self.state, self.input_tape, self.steps, self._get_view_code(self._prec_index), self._get_view_tape(),
                      self.global_var, status_bar=status_message)
            return None
        sleep_time = 1 / self.global_var["speed"] - 0.1
        i = 0
        if not self.ended:
            while self.code[i].current_state != self.state or self._remapped_char(self.code[i].current_symbol) != \
                  self.tape[self.tape_position]:
                i += 1
                if i == len(self.code):
                    self.ended = True
                    return None
        if self.global_var["instant"]:
            if self.ended:
                print(f"\n\nSteps: {self.steps}    Output: {''.join(self.tape).strip().upper()}")
                exit()
            else:
                threshold = 100000
                simulating_string = "Simulating... ─"
                if self.steps == 0:
                    print(f"\n{simulating_string}", end='', flush=True)
                elif self.steps == threshold:
                    info_string = "This program might be stuck in an infinite loop. To stop the simulation press \"q\""
                    print(f"\r{info_string}\n{simulating_string}", end='', flush=True)
                elif self.steps % (mod := 4000) == 0:
                    print_char = ['─', '\\', '|', '/'][(self.steps % (mod * 4)) // mod]
                    print(f"\b{print_char}", end='', flush=True)
        self.steps += 1
        self.tape[self.tape_position] = self._remapped_char(self.code[i].new_symbol)
        if not self.global_var["instant"] and not self.silent:
            Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(), self.global_var, writing=True)
            time.sleep(sleep_time)
        self.state = self.code[i].new_state
        if not self.global_var["instant"] and not self.silent:
            Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(), self.global_var)
            time.sleep(sleep_time)
        self._prec_index = i
        if self.tape_position == 0:
            self.tape = [" "] + self.tape
            self.tape_position += 1
        if self.tape_position == len(self.tape) - 1:
            self.tape = self.tape + [" "]
        if self.code[i].movement == ">":
            self.tape_position += 1
        elif self.code[i].movement == "<":
            self.tape_position -= 1
        if not self.global_var["instant"] and not self.silent:
            Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(), self.global_var)
            time.sleep(sleep_time)
            if self.breakpoints_list[self.code_map[i]] and self.global_var["breakpoints"] and not self.paused and not self.silent:
                self.pause()
