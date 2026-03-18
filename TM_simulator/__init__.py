import time
from .machine import TuringMachine as _TMachine, _get_error_message, _check_determinism
from .tuples import TuringTuple as _TMTuple
from .main import parse as _parse

def parse_tuples(input_string: str, is_file: bool = True, to_print: bool = False) -> list[_TMTuple] | list[str]:
    r"""
    Parses the given input and returns a parsed version of the tuples as a list. ``Input_string`` is the string that
    can either be the name of the file that contains the tuples or the tuples as a single string separated by \n based
    on the boolean ``is_file`` argument. It's recommended to read from a file though, hence the default True value of
    the argument. By default this function returns a list of TuringTuple objects, but you can set ``to_print`` to True
    to get back a print-friendly version of the parsed tuples that is however unusable in the machine.
    """
    code_tuples, *_, code_map, pars_errors = _parse(input_string, is_file)
    pars_errors.extend(_check_determinism(code_tuples))
    if len(pars_errors) > 0:
        errors = [(_get_error_message([error], code_map, is_instant=True, is_keyboard=False)) for error in pars_errors]
        class ParsingError(RuntimeError):
            pass
        raise ParsingError("\nSome errors were found while parsing the input: \n" + "\n".join(errors))
    if to_print:
        return ["(" + x.string_tuple + ")" for x in code_tuples]
    else:
        return code_tuples

def parse_breakpoints(input_string: str, is_file: bool = True) -> list[bool]:
    r"""
    Parses the given input and returns a parsed version of the breakpoints as a list. ``Input_string`` is the string that
    can either be the name of the file that contains the tuples or the tuples as a single string separated by \n based
    on the boolean ``is_file`` argument. It's recommended to read from a file though, hence the default True value of
    the argument. This function returns a list of boolean values, where ``True`` represents a breakpoint.
    """
    code_tuples, _, remapped_breakpoint_list, *_, code_map, pars_errors = _parse(input_string, is_file)
    pars_errors.extend(_check_determinism(code_tuples))
    if len(pars_errors) > 0:
        errors = [(_get_error_message([error], code_map, is_instant=True, is_keyboard=False)) for error in pars_errors]
        class ParsingError(RuntimeError):
            pass
        raise ParsingError("Some errors were found while parsing the input: \n" + "\n".join(errors))
    return remapped_breakpoint_list


class TuringMachine:
    r"""
    This is the main class of this module where the machine is managed. This is simply a wrapper of the base machine
    class cleaned up and remodelled to make it more user-friendly. The attributes of this class are:
     - ``state: str``: the name of the state the machine is in
     - ``tape: str``: the used part of the tape as a unique string
     - ``steps: int``: the number of elapsed steps since the beginning if the simulation
     - ``runtime: float``: the number of seconds, rounded to the milliseconds, the machine has taken that far to run the simulation
     - ``ended: bool``: whether the machine has halted the simulation
     - ``paused: bool``: whether the machine is in the paused state
    """

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
        self.tape = "".join(self._machine.tape).strip()
        self.steps = self._machine.steps
        self.ended = self._machine.ended
        self.paused = False
        self.threshold = 1_000_000
        self._machine.silent = True
        self.runtime = 0

    @classmethod
    def load_file(cls, filename: str, input_tape: str) -> "TuringMachine":
        r"""
        This is the primary method of setting up the machine, taking as arguments the ``filename`` of the file to
        parse and the ``input_tape`` of the machine. This method is useful when running single machine as it parses
        the input each time a new class is created with this.
        """
        parsed_tuples = parse_tuples(filename)
        parsed_breakpoints = parse_breakpoints(filename)
        return cls(parsed_tuples, parsed_breakpoints, input_tape)

    @classmethod
    def load_tuples(cls, parsed_tuples: list[_TMTuple], parsed_breakpoint: list[bool], input_tape: str) -> "TuringMachine":
        r"""
        This is an alternative method to load the data into the machine, passing the two parsed lists, ``parsed_tuples``
        and ``parsed_breakpoints``, along the ``input_tape`` of the machine. The two parsed lists can be retrieved using
        the two parsing functions of this module and this makes this method better to create multiple machines with the
        same tuple input: you can parse them one time and simply pass the list on each new instance of the class you
        want to create.
        """
        return cls(parsed_tuples, parsed_breakpoint, input_tape)

    def set_threshold(self, value: int) -> None:
        r"""
        Sets the threshold ``value`` of steps after which the machine stops running. This is done to avoid letting a machine
        run indefinitely on programs that might be stuck in an infinite cycle. You can set ``value`` to -1 to disable the
        threshold altogether.
        """
        self.threshold = value if value > 0 else float("inf")

    def run(self) -> None:
        r"""
        Runs the machine until the machine ends or the threshold value of steps is reached. When this function reaches
        the threshold it pauses the simulation. Calling ``run`` a second time will run the machine again for, at most,
        the number of steps indicated by the threshold. Running an ended machine has no effect.
        """
        start_time = time.perf_counter()
        consecutive_steps = 0
        while consecutive_steps < self.threshold and not (self.ended or self.paused):
            self._machine.step()
            self.ended = self._machine.ended
            self.paused = self._machine.paused
            consecutive_steps += 1
        self.state = self._machine.state
        self.tape = "".join(self._machine.tape).strip()
        self.steps = self._machine.steps
        self.runtime += round(time.perf_counter() - start_time, 6)

    def reset(self, tape: str = None) -> None:
        r"""
        Resets the machine status to the initial conditions. If ``tape`` argument is provided it will overwrite the old
        initial tape, else it will keep the same as the one declared on the class initialization.
        """
        self._machine.restart()
        self._machine.tape = list(tape) if tape is not None else self._machine.tape
        self.ended = False
        self._machine.paused = False

    def step(self, times: int = 1) -> None:
        r"""
        Steps the machine forward the amount of times set in the ``times`` argument. Note that stepping is not capped by
        the threshold like ``run`` and so it will run until the machine ends or the number of ``times`` is reached.
        Stepping an ended machine has no effect.
        """
        start_time = time.perf_counter()
        for _ in range(times):
            self._machine.step()
            if self._machine.ended:
                break
        self.state = self._machine.state
        self.tape = "".join(self._machine.tape).strip()
        self.steps = self._machine.steps
        self.ended = self._machine.ended
        self.runtime += round(time.perf_counter() - start_time, 6)

    def step_back(self, times: int = 1) -> None:
        r"""
        Steps the machine back the amount of times set in the ``times`` argument. Stepping an ended machine will take
        the machine back to the previous paused state you selected. Stepping a machine back before the starting state
        has no effect. Remember that because the turing machine cannot be step back like a normal forward step and so
        it has to run again from the start, up to the correct step. For this reason stepping back in long programs might
        take a while.
        """
        step_goal = self.steps - times if self.steps - times > 0 else 0
        self.reset()
        self.step(step_goal)

    def set_breakpoints(self, value: bool = True) -> None:
        r"""
        Enables or disables the breakpoints based on the argument ``value``
        """
        self._machine.global_var["breakpoints"] = value

    def print_status(self) -> None:
        r"""
        Prints some useful information regarding the state of the machine
        """
        formatted_runtime = (f"{self.runtime * 1000:.0f} ms" if self.runtime < 5 else f"{self.runtime:.3f} s") if \
                            self.runtime > 0.05 else f"{self.runtime * 1000:.3f} ms"
        print(f"Steps: {self.steps}    State: {self.state}    Tape: {self.tape.strip().upper()}    "
              f"Status: {'Ended' if self.ended else 'Paused'}    Time elapsed: {formatted_runtime}")

__all__ = [parse_tuples, parse_breakpoints, TuringMachine]
