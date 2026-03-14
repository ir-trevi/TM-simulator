from .machine import TuringMachine as _TMachine, _get_error_message, _check_determinism
from .tuples import TuringTuple as _TMTuple
from .main import parse as _parse

def parse_tuples(input_string: str, is_file: bool = True, to_print: bool = False):
    r"""
    Parses the given input and returns a parsed version of the tuples as a list. ``Input_string`` is the string that
    can either be the name of the file that contains the tuples or the tuples as a single string separated by \n based
    on the boolean ``is_file`` argument. It's recommended to read from a file though, hence the default True value of
    the argument. By default this function returns a list of TuringTuple objects, but you can set ``to_print`` to True
    to get back a print-friendly version of the parsed tuples that is however unusable in the machine.
    """
    code_tuples, *_, pars_errors = _parse(input_string, is_file)
    pars_errors.extend(_check_determinism(code_tuples))
    if len(pars_errors) > 0:
        for error in pars_errors:
            print(_get_error_message([error], is_instant=True, is_keyboard=False))
        exit()
    if to_print:
        return ["(" + x.string_tuple + ")" for x in code_tuples]
    else:
        return code_tuples

def parse_breakpoints(input_string: str, is_file: bool = True):
    code_tuples, _, remapped_breakpoint_list, *_, pars_errors = _parse(input_string, is_file)
    pars_errors.extend(_check_determinism(code_tuples))
    if len(pars_errors) > 0:
        for error in pars_errors:
            print(_get_error_message([error], is_instant=True, is_keyboard=False))
        exit()
    return remapped_breakpoint_list


class TuringMachine:

    def __init__(self, parsed_tuples: list[_TMTuple], parsed_breakpoints: list[bool], input_tape: str):
        if all([x.raw_string for x in parsed_tuples]):
            print("You can only pass a list of parsed tuples!")
            exit()
        self.parsed_tuples = parsed_tuples
        self.parsed_breakpoints = parsed_breakpoints
        self.input_tape = input_tape
        self._global_var = {
                  "speed": 10,
                  "tape_size": 30,
                  "code_size": 30,
                  "slim_tape": False,
                  "pars_errors": [],
                  "instant": True,
                  "breakpoints": False,
                  "debug": False,
                  "keyboard": False
                  }
        self._machine = _TMachine(input_tape, parsed_tuples, [False], parsed_breakpoints, [""], [0], [], self._global_var)
        self.state = self._machine.state
        self.tape = [x for x in "".join(self._machine.tape).strip()]
        self.steps = self._machine.steps
        self.ended = self._machine.ended
        self.paused = False
        self.threshold = 100000
        self._machine.silent = True

    @classmethod
    def load_file(cls, filename: str, input_tape: str):
        parsed_tuples = parse_tuples(filename)
        parsed_breakpoints = parse_breakpoints(filename)
        return cls(parsed_tuples, parsed_breakpoints, input_tape)

    @classmethod
    def load_tuples(cls, parsed_tuples: list[_TMTuple], parsed_breakpoint: list[bool], input_tape: str):
        return cls(parsed_tuples, parsed_breakpoint, input_tape)

    def set_threshold(self, value: int):
        self.threshold = value if value > 0 else float("inf")

    def run(self):
        consecutive_steps = 0
        while consecutive_steps < self.threshold and not (self.ended or self.paused):
            self._machine.step()
            self.ended = self._machine.ended
            self.paused = self._machine.paused
            consecutive_steps += 1
        self.state = self._machine.state
        self.tape = [x for x in "".join(self._machine.tape).strip()]
        self.steps = self._machine.steps

    def step(self, times: int = 1):
        for _ in range(times):
            self._machine.step()
        self.state = self._machine.state
        self.tape = [x for x in "".join(self._machine.tape).strip()]
        self.steps = self._machine.steps
        self.ended = self._machine.ended

    def step_back(self, times: int = 1):
        step_goal = self.steps - times if self.steps - times > 0 else 0
        self.__init__(self.parsed_tuples, self.parsed_breakpoints, self.input_tape)
        self.step(step_goal)

    def set_breakpoints(self, value: bool = True):
        self._machine.global_var["breakpoints"] = value

    def print_status(self):
        print(f"Steps: {self.steps}    State: {self.state}    Tape: {''.join(self.tape).strip().upper()}    "
              f"Status: {'Ended' if self.ended else 'Paused'}")

__all__ = [parse_tuples, parse_breakpoints, TuringMachine]
