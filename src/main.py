import os
import argparse
from tuples import TuringTuple
from machine import TuringMachine

def main():
    global_var = {"speed": 0,
                  "tape_size": 0,
                  "code_size": 0,
                  "slim_tape": 0,
                  "pars_errors": [],
                  "instant": False,
                  "breakpoints": False,
                  "debug": False}

    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.add_argument('--help', '-h', '-?', action='help', help=argparse.SUPPRESS)
    arg_parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    arg_parser.add_argument("filename", type=str, help="Name of the file with the tuples")
    arg_parser.add_argument("input", type=str, help="The initial tape of the machine", default=" ")
    arg_parser.add_argument("--speed", "-s", dest="speed", metavar="<int>", type=int, help="set the step speed of the simulation, in a range from 1 to 10", default=9)
    arg_parser.add_argument("--breakpoints", "-b", dest="breakpoints", help="enable the breakpoints, pausing the simulation when one is encountered", action="store_true")
    arg_parser.add_argument("--instant", "-i", dest="instant", help="return the final tape when the machine stops, without the interface", action="store_true")
    arg_parser.add_argument("--auto", "-a", dest="auto", help="finds the best interface options based on the terminal size", action="store_true")
    arg_parser.add_argument("--keyboard", "-k", dest="keyboard", help="enables keyboard to control the simulation (still buggy)", action="store_true")
    arg_parser.add_argument("--slim", dest="slim", help="make the cells in the tape smaller, useful when the terminal window is small", action="store_true")
    arg_parser.add_argument("--csize", dest="csize", metavar="<int>", type=int, help="set the size of the left code panel, measured in characters", default=None)
    arg_parser.add_argument("--tsize", dest="tsize", metavar="<int>", type=int, help="set the number of cells visible on the tape", default=None)
    arg_parser.usage = ("tm-simulator [filename <path>] [input <string>] [-s | --speed <int>] [-b | --breakpoints] [-i | --instant] [-a | --auto] [-k | --keyboard] [--slim] [--csize <int>] [--tsize <int>] \n"
                        "usage: tm-simulator [-h | --help] ")
    args = arg_parser.parse_args()
    global_var["debug"] = args.debug
    global_var["speed"] = args.speed
    global_var["tape_size"] = args.tsize
    global_var["code_size"] = args.csize
    global_var["slim_tape"] = args.slim
    global_var["breakpoints"] = args.breakpoints
    global_var["instant"] = args.instant
    global_var["keyboard"] = args.keyboard
    auto = args.auto
    filename = args.filename
    input_tape = args.input if args.input else " "

    if global_var["speed"] < 1 or global_var["speed"] > 10:
        print("The simulation speed is not within the range")
        exit()
    if not (auto or (global_var["code_size"] or global_var["tape_size"]) or global_var["instant"]):
        print("Either auto mode or the specific sizes needs to be specified")
        exit()
    if not global_var["instant"] and not global_var["debug"]:
        try:
            length, height = tuple(os.get_terminal_size())
        except OSError:
            print("This script is not compatible with the terminal you're using")
            exit()
        if height < 20 or length < 120:
            print("The terminal window is not large enough")
            exit()
        if not auto:
            if global_var["code_size"] < 0 or global_var["tape_size"] <= 0:
                print("The specified sizes are negative")
                exit()
            if global_var["tape_size"] % 2 == 0:
                print("The numbers of cells needs to be an odd number")
                exit()
            elif global_var["code_size"] + global_var["tape_size"] * (2 if global_var["slim_tape"] else 4) + 5 > length:
                print("The terminal window is not large enough for these settings")
                exit()
        else:
            if length > 172:
                global_var["slim_tape"] = False
                global_var["tape_size"] = 33
                global_var["code_size"] = length - global_var["tape_size"] * 4 - 14 if global_var["code_size"] != 0 else 0
            else:
                global_var["slim_tape"] = True
                global_var["tape_size"] = 33
                global_var["code_size"] = length // 4 if global_var["code_size"] != 0 else 0

    try:
        with open(filename) as file:
            raw_tuples = [x.removesuffix('\n') for x in file]
    except FileNotFoundError:
        print("The file with the program was not found (paths are not supported, change directory and then run the script there)")
        exit()

    code_tuples = []
    code_map = []
    breakpoint_list = []
    pars_errors = []
    for i, raw_tuple in enumerate(raw_tuples):
        parsed_tuples = TuringTuple(raw_tuple, i, True)
        pars_errors.extend(parsed_tuples.pars_errors) if parsed_tuples.pars_errors else None
        parsed_tuples = [x for x in parsed_tuples.expanded_tuple if x != ""]
        code_tuples.extend([TuringTuple(x, i, False) for x in parsed_tuples])
        code_map.extend([i for _ in parsed_tuples])
        breakpoint_list.append(TuringTuple(raw_tuple, i, True).has_breakpoint())
    turing_machine = TuringMachine(input_tape, code_tuples, breakpoint_list, raw_tuples, code_map, pars_errors, global_var)
    if not global_var["instant"] and global_var["keyboard"]:
        import keyboard
        keyboard.on_press_key("q", lambda _: turing_machine.terminate()) if not global_var["instant"] else None
        keyboard.on_press_key("space", lambda _: turing_machine.pause())
        keyboard.on_press_key("right", lambda _: turing_machine.move_right())
        keyboard.on_press_key("left", lambda _: turing_machine.move_left())
        [keyboard.on_press_key(x+1, lambda _, y=x: turing_machine.change_speed(y)) for x in range(11)[1:]]
        keyboard.on_press_key("r", lambda _: turing_machine.restart())

    try:
        while True:
            turing_machine.step()
    except KeyboardInterrupt:
        print()
        exit()

if __name__ == "__main__":
    main()
