class TuringTuple:

    def __init__(self, string_tuple: str, index: int, raw_string: bool = False) -> None:
        self.raw_string = raw_string
        self.string_tuple = string_tuple
        self.index = index
        self.pars_errors = []
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
                self.pars_errors.append((self.index, 'incompatible_dot_limiters'))
            elif not current_char.isalnum() or not notation_end_char.isalnum():
                self.pars_errors.append((self.index, 'symbol_dot_limiter'))
            elif ord(current_char) > ord(notation_end_char):
                self.pars_errors.append((self.index, 'descending_order'))
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
            self.pars_errors.append((self.index, 'empty_class'))
        elif class1_start_count != class1_end_count or class2_start_count != class2_end_count:
            self.pars_errors.append((self.index, 'missing_class_limiters'))
        elif class1_start_count > 1 or class1_end_count > 1 or class2_start_count > 1 or class2_end_count > 1:
            self.pars_errors.append((self.index, 'multiple_class'))
        class_string1 = self._find(input_string, '[', ']', '\\', '\\', start_included=False, end_included=False)
        class_string2 = self._find(input_string, '{', '}', '\\', '\\', start_included=False, end_included=False)
        if class1_start_count != 0 and class2_start_count != 0:
            self.pars_errors.append((self.index, 'multiple_class_types'))
        elif not class_string1 and not class_string2:
            self.pars_errors.append((self.index, 'empty_class'))
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
                self.pars_errors.append((self.index, 'opening_char_missing'))
            if self.string_tuple[-1] != ")":
                self.pars_errors.append((self.index, 'closing_char_missing'))
            clean_tuple = self._find(self.string_tuple, "(", ")", "\\", "\\", start_included=False, end_included=False)
            split_tuple = self._split(clean_tuple, ",", "\\")
            if len(split_tuple) != 5:
                self.pars_errors.append((self.index, 'incorrect_arguments_amount'))
            if not all([bool(x) for x in split_tuple]):
                self.pars_errors.append((self.index, 'empty_rule'))
            split_tuple = [self._exclusion_expansion(self._double_dot_expansion(x)) for x in split_tuple]
            split_expanded_tuple = [self._class_expansion(x) for x in split_tuple]
            current_symbol = split_expanded_tuple[1][0]
            new_symbol = split_expanded_tuple[3][0]
            movement = split_expanded_tuple[4][0]
            if (not all([len(x) == 1 or (len(x) == 2 and x[0] == "\\") for x in current_symbol]) and len(current_symbol) != 1) or \
               (not all([len(x) == 1 or (len(x) == 2 and x[0] == "\\") for x in new_symbol]) and len(new_symbol) != 1):
                self.pars_errors.append((self.index, 'multiple_symbols'))
            current_symbol = self._split_each(current_symbol[0], "\\") if len(current_symbol[0]) != 1 else current_symbol
            new_symbol = self._split_each(new_symbol[0], "\\") if len(new_symbol[0]) != 1 else new_symbol
            movement = self._split_each(movement[0], "\\") if len(movement[0]) != 1 else movement
            split_expanded_tuple[1][0] = current_symbol
            split_expanded_tuple[3][0] = new_symbol
            split_expanded_tuple[4][0] = movement
            current_state, _, new_state, _, _ = [x[0] for x in split_expanded_tuple]
            if not all([x in [">", "<", "-"] for x in movement]):
                self.pars_errors.append((self.index, 'unrecognised_movement'))
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
                self.pars_errors.append((self.index, 'different_class_sizes'))
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
        except Exception:
            return ["(0,0,0,0,0)"]

    def has_breakpoint(self) -> bool:
        if self.string_tuple == "":
            return False
        if self.string_tuple.strip()[0] == "!":
            return True
        else:
            return False
