import os
import time
import argparse


class TuringTuple:

    def __init__(self, string_tuple: str, index: int, raw_string: bool = False) -> None:
        self.raw_string = raw_string
        self.string_tuple = string_tuple
        self.index = index
        if not raw_string:
            self.current_state, self.current_symbol, self.new_state, self.new_symbol, self.movement = self._split(
                self.string_tuple, ',', '\\')
        else:
            self.expanded_tuple = self.expand()

    def _split(self, input_string: str, split_char: str, special_char: str) -> list[str]:
        if split_char not in input_string:
            return [input_string]
        index = 0
        char_found = False
        while index < len(input_string) and not char_found:
            current_char = input_string[index]
            if current_char == special_char:
                index += 1
            elif current_char == split_char:
                char_found = True
            index += 1
        return [input_string[:index - 1]] + self._split(input_string[index:], split_char, special_char)

    def _split_each(self, input_string: str, special_char: str) -> list[str]:
        if special_char not in input_string:
            return [x for x in input_string]
        buffer_string = ""
        return_list = []
        for char in input_string:
            buffer_string += char
            if char == special_char and len(buffer_string) < 2:
                continue
            else:
                return_list.append(buffer_string)
                buffer_string = ""
        return return_list

    def _find(self, input_string: str, start_char: str, end_char: str, special_start_char: str, special_end_char: str,
              start_included: bool, end_included: bool) -> str:
        if start_char not in input_string or end_char not in input_string:
            return ''
        start_index = 0
        char_found = False
        while start_index < len(input_string) and not char_found:
            current_char = input_string[start_index]
            if current_char == special_start_char:
                start_index += 2
            elif current_char == start_char:
                char_found = True
            else:
                start_index += 1
        end_index = 0
        char_found_index = 0
        while end_index < len(input_string):
            current_char = input_string[end_index]
            if current_char == special_end_char:
                end_index += 1
            elif current_char == end_char:
                char_found_index = end_index
            end_index += 1
        else:
            start_index = start_index if start_included else start_index + 1
            char_found_index = char_found_index + 1 if end_included else char_found_index
            return input_string[start_index:char_found_index]

    def _count(self, input_string: str, count_char: str, special_char: str) -> int:
        counter = 0
        index = 0
        while index < len(input_string):
            current_char = input_string[index]
            if current_char == special_char:
                index += 1
            elif current_char == count_char:
                counter += 1
            index += 1
        return counter

    def _remove_comment(self) -> None:
        buffer_string = ""
        skip_char = False
        for char in self.string_tuple:
            if char != "\\" and char != "#":
                buffer_string += char
            elif skip_char:
                buffer_string += char
                skip_char = False
            elif char == "\\" and not skip_char:
                buffer_string += char
                skip_char = True
            elif char == "#" and not skip_char:
                break
        self.string_tuple = buffer_string

    def _double_dot_expansion(self, input_string: str) -> str:
        if '..' not in input_string:
            return input_string
        double_dot_count = input_string.count('..')
        double_dot_list = []
        connection_list = []
        while double_dot_count > 0:
            double_dot_index = input_string.index('..') - 1
            if double_dot_index + 4 > len(input_string):
                connection_list.append(input_string)
            elif double_dot_index == -1:
                input_string = input_string[3:]
            else:
                double_dot_list.append(input_string[double_dot_index:double_dot_index + 4])
                connection_list.append(input_string[:double_dot_index])
                input_string = input_string[double_dot_index + 4:]
            double_dot_count -= 1
        return_list = []
        for expression in double_dot_list:
            expansion_string = ''
            current_char = expression[0]
            notation_end_char = expression[-1]
            if current_char.isalpha() != notation_end_char.isalpha():
                pars_errors.append((self.index, 'incompatible_dot_limiters'))
            elif not current_char.isalnum() or not notation_end_char.isalnum():
                pars_errors.append((self.index, 'symbol_dot_limiter'))
            elif ord(current_char) > ord(notation_end_char):
                pars_errors.append((self.index, 'descending_order'))
            elif current_char != '.' or notation_end_char != '.':
                ord_current_char = ord(current_char)
                ord_notation_end = ord(notation_end_char)
                while ord_current_char <= ord_notation_end:
                    expansion_string += chr(ord_current_char)
                    ord_current_char += 1
                return_list.append(expansion_string)
        merged_list = []
        return_list = [''] if not return_list else return_list
        while return_list or connection_list:
            merged_list.append(connection_list.pop(0))
            merged_list.append(return_list.pop(0))
        return ''.join(merged_list) + input_string

    def _exclusion_expansion(self, input_string: str) -> str:
        special_char = '\\-()^,#[]{}'
        normal_char = '-abcdefghijklmnopqrstuvwxyz0123456789!?£$%&|§:_.\"\'=*+;<>/@'
        exception_string = self._find(input_string, '^', input_string[-1], '\\', '', start_included=False,
                                      end_included=True)
        exception_string = self._split(exception_string, ',', '\\')[0] if exception_string else ""
        if exception_string == '':
            return input_string
        special_char_found = False
        for index in range(len(exception_string)):
            character = exception_string[index]
            if character == '\\' and not special_char_found:
                special_char_found = True
                continue
            elif character in special_char and special_char_found:
                special_char = special_char.replace(character, '')
            else:
                normal_char = normal_char.replace(character, '')
        return normal_char + '\\' + '\\'.join(special_char)

    def _class_expansion(self, input_string: str) -> list[list[str], int]:
        class1_start_count = self._count(input_string, '[', '\\')
        class1_end_count = self._count(input_string, ']', '\\')
        class2_start_count = self._count(input_string, '{', '\\')
        class2_end_count = self._count(input_string, '}', '\\')
        if class1_start_count == class1_end_count == 0 and class2_start_count == class2_end_count == 0:
            return [[input_string], 0]
        elif input_string == '[]' or input_string == '{}':
            pars_errors.append((self.index, 'empty_class'))
        elif class1_start_count != class1_end_count or class2_start_count != class2_end_count:
            pars_errors.append((self.index, 'missing_class_limiters'))
        elif class1_start_count > 1 or class1_end_count > 1 or class2_start_count > 1 or class2_end_count > 1:
            pars_errors.append((self.index, 'multiple_class'))
        class_string1 = self._find(input_string, '[', ']', '\\', '\\', start_included=False, end_included=False)
        class_string2 = self._find(input_string, '{', '}', '\\', '\\', start_included=False, end_included=False)
        if class1_start_count != 0 and class2_start_count != 0:
            pars_errors.append((self.index, 'multiple_class_types'))
        elif not class_string1 and not class_string2:
            pars_errors.append((self.index, 'empty_class'))
        class_type = 1 if class_string1 else 2
        class_string = class_string1 if class_string1 else class_string2
        class_start_index = input_string.find(class_string)
        class_end_index = class_start_index + len(class_string)
        first_part = input_string[:class_start_index - 1]
        last_part = input_string[class_end_index + 1:]
        return_list = []
        for character in class_string:
            return_list.append(first_part + character + last_part)
        return [return_list, class_type]

    def expand(self) -> list[str]:
        try:
            self._remove_comment()
            self.string_tuple = self.string_tuple.lower().replace(" ", "")
            if self.string_tuple == "":
                return [""]
            if self.string_tuple[0] != "(" and self.string_tuple[:2] != "!(":
                pars_errors.append((self.index, 'opening_char_missing'))
            if self.string_tuple[-1] != ")":
                pars_errors.append((self.index, 'closing_char_missing'))
            clean_tuple = self._find(self.string_tuple, "(", ")", "\\", "\\", start_included=False, end_included=False)
            split_tuple = self._split(clean_tuple, ",", "\\")
            if len(split_tuple) != 5:
                pars_errors.append((self.index, 'incorrect_arguments_amount'))
            if not all([bool(x) for x in split_tuple]):
                pars_errors.append((self.index, 'empty_rule'))
            split_tuple = [self._exclusion_expansion(self._double_dot_expansion(x)) for x in split_tuple]
            split_expanded_tuple = [self._class_expansion(x) for x in split_tuple]
            current_symbol = split_expanded_tuple[1][0]
            new_symbol = split_expanded_tuple[3][0]
            movement = split_expanded_tuple[4][0]
            if (not all([len(x) == 1 or (len(x) == 2 and x[0] == "\\") for x in current_symbol]) and len(current_symbol) != 1) or \
               (not all([len(x) == 1 or (len(x) == 2 and x[0] == "\\") for x in new_symbol]) and len(new_symbol) != 1):
                pars_errors.append((self.index, 'multiple_symbols'))
            current_symbol = self._split_each(current_symbol[0], "\\") if len(current_symbol[0]) != 1 else current_symbol
            new_symbol = self._split_each(new_symbol[0], "\\") if len(new_symbol[0]) != 1 else new_symbol
            movement = self._split_each(movement[0], "\\") if len(movement[0]) != 1 else movement
            split_expanded_tuple[1][0] = current_symbol
            split_expanded_tuple[3][0] = new_symbol
            split_expanded_tuple[4][0] = movement
            current_state, _, new_state, _, _ = [x[0] for x in split_expanded_tuple]
            if not all([x in [">", "<", "-"] for x in movement]):
                pars_errors.append((self.index, 'unrecognised_movement'))
            class_0_elements = [x for x in split_expanded_tuple if x[1] == 0]
            class_1_elements = [x for x in split_expanded_tuple if x[1] == 1]
            class_2_elements = [x for x in split_expanded_tuple if x[1] == 2]
            class_0 = [x[1] == 0 for x in split_expanded_tuple]
            class_1 = [x[1] == 1 for x in split_expanded_tuple]
            class_2 = [x[1] == 2 for x in split_expanded_tuple]
            max_len_class_0 = max([len(y[0]) for y in split_expanded_tuple if y[1] == 0], default=1)
            max_len_class_1 = max([len(y[0]) for y in split_expanded_tuple if y[1] == 1], default=1)
            max_len_class_2 = max([len(y[0]) for y in split_expanded_tuple if y[1] == 2], default=1)
            if not all([len(x[0]) == max_len_class_2 or len(x[0]) == 1 for x in class_2_elements]) or \
               not all([len(x[0]) == max_len_class_1 or len(x[0]) == 1 for x in class_1_elements]) or \
               not all([len(x[0]) == max_len_class_0 or len(x[0]) == 1 for x in class_0_elements]):
                pars_errors.append((self.index, 'different_class_sizes'))
            return_list = []
            for i_2 in range(max_len_class_2):
                current_state_loop = current_state[i_2 if len(current_state) != 1 else 0] if class_2[0] else None
                current_symbol_loop = current_symbol[i_2 if len(current_symbol) != 1 else 0] if class_2[1] else None
                new_state_loop = new_state[i_2 if len(new_state) != 1 else 0] if class_2[2] else None
                new_symbol_loop = new_symbol[i_2 if len(new_symbol) != 1 else 0] if class_2[3] else None
                movement_loop = movement[i_2 if len(movement) != 1 else 0] if class_2[4] else None
                for i_1 in range(max_len_class_1):
                    current_state_loop = current_state[i_1 if len(current_state) != 1 else 0] if class_1[0] else current_state_loop
                    current_symbol_loop = current_symbol[i_1 if len(current_symbol) != 1 else 0] if class_1[1] else current_symbol_loop
                    new_state_loop = new_state[i_1 if len(new_state) != 1 else 0] if class_1[2] else new_state_loop
                    new_symbol_loop = new_symbol[i_1 if len(new_symbol) != 1 else 0] if class_1[3] else new_symbol_loop
                    movement_loop = movement[i_1 if len(movement) != 1 else 0] if class_1[4] else movement_loop
                    for i_0 in range(max_len_class_0):
                        current_state_loop = current_state[i_0 if len(current_state) != 1 else 0] if class_0[0] else current_state_loop
                        current_symbol_loop = current_symbol[i_0 if len(current_symbol) != 1 else 0] if class_0[1] else current_symbol_loop
                        new_state_loop = new_state[i_0 if len(new_state) != 1 else 0] if class_0[2] else new_state_loop
                        new_symbol_loop = new_symbol[i_0 if len(new_symbol) != 1 else 0] if class_0[3] else new_symbol_loop
                        movement_loop = movement[i_0 if len(movement) != 1 else 0] if class_0[4] else movement_loop
                        return_list.append(','.join([current_state_loop, current_symbol_loop, new_state_loop,
                                                     new_symbol_loop, movement_loop]))
            return return_list
        except Exception as e:
            return ["(0,0,0,0,0)"]

    def has_breakpoint(self) -> bool:
        if self.string_tuple == "":
            return False
        if self.string_tuple.strip()[0] == "!":
            return True
        else:
            return False

class TuringMachine:

    def __init__(self, input_tape: str, code: list[TuringTuple], breakpoints: list[bool], raw_code: list[str],
                 code_map: list[int]) -> None:
        self.input_tape = input_tape
        self.code = code
        self.raw_code = raw_code
        self.code_map = code_map
        self.breakpoints = breakpoints
        self.state = "0"
        self.tape_position = 0
        self.tape = list(input_tape)
        self.steps = 0
        self._prec_index = 0
        self._first_view = True
        self._check_determinism()
        if len(pars_errors) != 0:
            is_direct = isinstance(pars_errors[0][0], list)
            error_line = pars_errors[0][0][0] if is_direct else pars_errors[0][0]
            if not instant:
                interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(error_line, not is_direct),
                                      self._get_view_tape(), False, self._get_error_message())
                interface.show()
                time.sleep(60)
            else:
                print(self._get_error_message())
            exit()

    def _check_determinism(self) -> None:
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
                pars_errors.append((index_list, 'non_deterministic'))

    def _get_error_message(self) -> str:
        error_code = pars_errors[0][1]
        multiple_lines = isinstance(pars_errors[0][0], list)
        error_lines = ", ".join(list(dict.fromkeys([str(self.code_map[i]) for i in pars_errors[0][0]]))[:5]) if multiple_lines else pars_errors[0][0]
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
        return_list = []
        code_height = tuple(os.get_terminal_size())[1] - 6
        code_index = self.code_map[index] if not direct else index
        for i in range(code_index - code_height // 2 + 1, code_index + code_height // 2 + 2):
            try:
                if i < 0:
                    raise IndexError
                code = self.raw_code[i].replace("!(", "(", 1) if self.raw_code[i].strip()[:2] == "!(" else self.raw_code[i]
                return_list.append((self.breakpoints[i], code))
            except IndexError:
                return_list.append((False, ""))
        return return_list

    def _get_view_tape(self) -> str:
        return_string = ""
        for i in range(self.tape_position - tape_size // 2, self.tape_position + tape_size // 2 + 1):
            try:
                if i < 0:
                    raise IndexError
                return_string += self.tape[i]
            except IndexError:
                return_string += " "
        return return_string

    def _remapped_char(self, char: str) -> str:
        special_view_chars = [' ', '\\', '-', '(', ')', '^', ',', '#', '[', ']', '{', '}']
        special_code_char = ['-', '\\\\', '\\-', '\\(', '\\)', '\\^', '\\,', '\\#', '\\[', '\\]', '\\{', '\\}']
        current_char = char
        if current_char in special_code_char:
            current_char = special_view_chars[special_code_char.index(current_char)]
        return current_char

    def step(self) -> None:
        sleep_time = 1 / speed - 0.1 if not instant else 0
        i = 0
        while (self.code[i].current_state != self.state or self._remapped_char(self.code[i].current_symbol) !=
               self.tape[self.tape_position]) and i < len(self.code):
            i += 1
            if i == len(self.code):
                if not instant:
                    interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(self._prec_index),
                                          self._get_view_tape(), False, "Simulation ended! (Press Ctrl+C to exit)")
                    interface.show()
                    time.sleep(60)
                else:
                    print(f"\nSteps: {self.steps}    Output: {''.join(self.tape).strip().upper()}")
                exit()
        self.steps += 1
        if not instant:
            interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(),
                                  False)
            interface.show()
        if self._first_view and not instant:
            self._first_view = False
            time.sleep(1)
        if instant:
            threshold = 100000
            if self.steps == 1:
                print("\nSimulating... ─", end='')
            elif self.steps % 2000 == 0 and self.steps < threshold:
                print_char = ['\\', '|', '/', '─'][(self.steps % 8000) // 2000]
                print(f"\b{print_char}", end='', flush=True)
            elif self.steps == threshold:
                print("\nThis program might be stuck in an infinite loop. To stop the simulation press Ctrl + C", flush=True)
        time.sleep(sleep_time)
        self.tape[self.tape_position] = self._remapped_char(self.code[i].new_symbol)
        if not instant:
            interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(),
                                  True)
            interface.show()
        time.sleep(sleep_time)
        self.state = self.code[i].new_state
        if not instant:
            interface = Interface(self.state, self.input_tape, self.steps, self._get_view_code(i), self._get_view_tape(),
                                  False)
            interface.show()
        self._prec_index = i
        time.sleep(sleep_time)
        if self.tape_position == 0:
            self.tape = [" "] + self.tape
            self.tape_position += 1
        if self.tape_position == len(self.tape) - 1:
            self.tape = self.tape + [" "]
        if self.code[i].movement == ">":
            self.tape_position += 1
        elif self.code[i].movement == "<":
            self.tape_position -= 1

class Interface:

    def __init__(self, state: str, input_tape: str, steps: int, view_code: list[tuple[bool, str]], view_tape: str,
                 writing: bool, status_bar: str = None) -> None:
        self.state = state
        self.input_tape = input_tape
        self.steps = steps
        self.view_code = view_code
        self.view_tape = view_tape
        self.writing = writing
        self.code_size = code_size
        self.status_bar = status_bar

    def show(self) -> None:
        def show_code(index: int, arrow: bool) -> str:
            return (f" {'->' if arrow else '  '} {'!' if self.view_code[index - 3][0] else ' '}"
                    f" {self.view_code[index - 3][1]}").ljust(self.code_size - 1)[:self.code_size - 1] + "║\n"
        length, height = tuple(os.get_terminal_size())
        if self.code_size + tape_size * (2 if slim_tape else 4) + 10 > length or height < 20 or length < 105:
            os.system("cls" if os.name == "nt" else "clear")
            print("The terminal window size was changed while the simulator was running and the new size is not supported")
            exit()

        c = (height - 8) // 2
        buffer_string = ''
        for i in range(height):
            if i == 0:
                buffer_string += f"╔{'═' * (length - 2)}╗"
            elif i == 1:
                buffer_string += f"║{'Turing Machine Simulator'.center(length)[1:-1]}║"
            elif i == 2:
                buffer_string += f"╠{'═' * (length - self.code_size - 2)}╤{'═' * (self.code_size - 1)}╣"
            elif i == c - 6:
                upper_part = f"┌{'─' * (tape_size - 2)}┐"
                buffer_string += f"║{upper_part.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c - 5:
                text = f"│{self.state.center(tape_size - 2)}│"
                buffer_string += f"║{text.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c - 4:
                lower_part = f"└{'─' * (tape_size - 2)}┘"
                buffer_string += f"║{lower_part.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c + 2:
                buffer_string += f"║{'│'.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c + 3:
                arrow_tip = '*' if self.writing else 'V'
                buffer_string += f"║{arrow_tip.center(length - self.code_size - 2)}│" + show_code(i, True)
            elif i == c + 4:
                upper_tape = f"─{('┬─' if slim_tape else '─┬──') * (tape_size + 1)}"
                buffer_string += f"║{upper_tape.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c + 5:
                tape_content = f"  │ {' │ '.join(self.view_tape.upper())} │  "
                tape_content = f" {tape_content.replace(' │ ', '│')} " if slim_tape else tape_content
                buffer_string += f"║{tape_content.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == c + 6:
                upper_tape = f"─{('┴─' if slim_tape else '─┴──') * (tape_size + 1)}"
                buffer_string += f"║{upper_tape.center(length - self.code_size - 2)}│" + show_code(i, False)
            elif i == height - 5:
                buffer_string += f"╟{'─' * (length - self.code_size - 2)}┤" + show_code(i, False)
            elif i == height - 4:
                buffer_string += f"║  Input: {self.input_tape.upper().ljust(length - self.code_size - 10)}"\
                                 [:length - self.code_size - 1] + "│" + show_code(i, False)
            elif i == height - 3:
                buffer_string += f"╠{'═' * (length - self.code_size - 2)}╧{'═' * (self.code_size - 1)}╣"
            elif i == height - 2:
                text = f"  Simulation speed: {speed}   Steps counter: {self.steps}    " + \
                       ("Press Ctrl + C at any moment to stop the simulation... " if not self.status_bar else
                        self.status_bar)
                buffer_string += f"║{text.ljust(length - 2)}║"
            elif i == height - 1:
                buffer_string += f"╚{'═' * (length - 2)}╝"
            else:
                buffer_string += f"║{' ' * (length - self.code_size - 2)}│" + show_code(i, False)
        print(buffer_string, end='', flush=True)

def main():
    global speed
    global tape_size
    global code_size
    global slim_tape
    global pars_errors
    global instant

    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.add_argument('--help', '-h', action='help', help=argparse.SUPPRESS)
    arg_parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    arg_parser.add_argument("filename", type=str, help="Name of the file with the tuples")
    arg_parser.add_argument("input", type=str, help="The initial tape of the machine", default=" ")
    arg_parser.add_argument("--speed", "-s", dest="speed", metavar="<int>", type=int, help="set the step speed of the simulation, in a range from 1 to 10", default=9)
    arg_parser.add_argument("--breakpoints", "-b", dest="breakpoints", help="enable the breakpoints, pausing the simulation when one is encountered", action="store_true")
    arg_parser.add_argument("--instant", "-i", dest="instant", help="return the final tape when the machine stops, without the interface", action="store_true")
    arg_parser.add_argument("--auto", "-a", dest="auto", help="finds the best interface options based on the terminal size", action="store_true")
    arg_parser.add_argument("--slim", dest="slim", help="make the cells in the tape smaller, useful when the terminal window is small", action="store_true")
    arg_parser.add_argument("--csize", dest="csize", metavar="<int>", type=int, help="set the size of the left code panel, measured in characters", default=None)
    arg_parser.add_argument("--tsize", dest="tsize", metavar="<int>", type=int, help="set the number of cells visible on the tape", default=None)
    arg_parser.usage = ("tm-simulator [filename <path>] [input <string>] [-s | --speed <int>] [-b | --breakpoints] [-i | --instant] [-a | --auto] [--slim] [--csize <int>] [--tsize <int>] \n"
                        "usage: tm-simulator [-h | --help] ")
    args = arg_parser.parse_args()
    debug = args.debug
    speed = args.speed
    tape_size = args.tsize
    code_size = args.csize
    slim_tape = args.slim
    breakpoints = args.breakpoints
    instant = args.instant
    auto = args.auto
    input_tape = args.input if args.input else " "
    pars_errors = []

    example_folder = os.path.join(os.path.dirname(__file__), "examples")
    match args.filename:
        case "count":
            filename = os.path.join(example_folder, "dots.txt")
        case "even-odd":
            filename = os.path.join(example_folder, "even-odd.txt")
        case "palindrome":
            filename = os.path.join(example_folder, "palindrome.txt")
        case "reverse":
            filename = os.path.join(example_folder, "reverse.txt")
        case "bin-dec":
            filename = os.path.join(example_folder, "bin-dec.txt")
        case _:
            filename = args.filename

    if speed < 1 or speed > 10:
        print("The simulation speed is not within the range")
        exit()
    if (not auto and not (code_size or tape_size)) and not instant:
        print("Either auto mode or the specific sizes needs to be specified")
        exit()
    if not instant and not debug:
        try:
            length, height = tuple(os.get_terminal_size())
        except OSError:
            print("This script is not compatible with the terminal you're using")
            exit()
        if height < 20 or length < 140:
            print("The terminal window is not large enough")
            exit()
        if not auto:
            if tape_size % 2 == 0:
                print("The numbers of cells needs to be an odd number")
                exit()
            elif code_size + tape_size * (2 if slim_tape else 4) + 5 > length:
                print("The terminal window is not large enough for these settings")
                exit()
        else:
            if length > 172:
                slim_tape = False
                tape_size = 33
                code_size = length - tape_size * 4 - 14
            else:
                slim_tape = True
                tape_size = 33
                code_size = length // 4

    with open(filename) as file:
        raw_tuples = [x.removesuffix('\n') for x in file]
    code_tuples = []
    code_map = []
    breakpoint_list = []
    for i, raw_tuple in enumerate(raw_tuples):
        parsed_tuples = TuringTuple(raw_tuple, i, True).expanded_tuple
        parsed_tuples = [x for x in parsed_tuples if x != ""]
        code_tuples.extend([TuringTuple(x, i, False) for x in parsed_tuples])
        code_map.extend([i for x in parsed_tuples])
        breakpoint_list.append(TuringTuple(raw_tuple, i, True).has_breakpoint())
    try:
        machine = TuringMachine(input_tape, code_tuples, breakpoint_list, raw_tuples, code_map)
        while True:
            machine.step()
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()
