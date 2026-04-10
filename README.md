# Turing Machine Simulator

A Turing Machine Simulator coded in Python from scratch by me. It uses a terminal interface to show what the machine is doing.

<img width="1538" height="823" alt="turing simulator 2" src="https://github.com/user-attachments/assets/6ee778df-ca1a-4100-8fbe-b5238f3cf35d" />

It shares the syntax and a similar interface with Vittorio Gambaletta's simulator ([VittGam/JSTMSimulator](https://github.com/VittGam/JSTMSimulator)), but it adds new features such as:
- Deterministic behaviour check
- Faster simulation speeds (~1M steps/sec)
- Instant simulation
- Breakpoints
- Stepping (backward and forward)

## Run from the command line
First, install the module running this command:
```terminaloutput
pip install git+https://github.com/ir-trevi/TM-simulator
```
Then you can use this command to run the simulator:
```terminaloutput
tm-simulator [filename <file>] [input <string>] -a
```
- `filename`: the name of the `.txt` program file that contains the tuples that define the machine behaviour
- `input`: the characters on the initial tape. It's better to enclose the input in quotes (single or doubles)

There are also some optional arguments:
- `--speed | -s <int>`: sets the step speed of the simulation, in a range from `1` to `10`, default is `9`
- `--breakpoints | -b`: enables the breakpoints, pausing the simulation when one is encountered
- `--instant | -i`: returns the final tape when the machine stops, without the interface
- `--auto | -a`: finds the best interface options based on the terminal size
- `--keyboard | -k`: enables the keyboard controls for the machine however, even though this enables full control of the simulation, it is not recommended to use it since the module it is based on is a bit buggy and not maintained any more 
- `--slim`: makes the cells in the tape smaller, useful when the terminal window is small
- `--csize <int>`: sets the size of the left code panel, measured in characters. It can also be sets to `0` and no code will be displayed
- `--tsize <int>`: sets the number of cells visible on the tape

Either `--auto | -a` or both `--csize <int>` and `--tsize <int>` need to be included in the command.  
When `--auto | -a` is selected it will overwrite all the other settings (`--csize`, `--tsize`, `--slim`) except when `--csize` is `0` to disable code.

When `--instant | -i` is selected, all the other interface-related setting will be discarded and it's also mutually exclusive with `--keyboard | -k`.

### Use the simulator
With `--keyboard | -k` selected, when the command to run the simulator is entered, the interface shows up and the simulation is `paused`. There are 3 possible states of the simulator:
- `Running`: in this state the simulator can be paused only by pressing the `spacebar`
- `Paused`: in this state there are some actions available such as:
  - changing the speed, using the numbers from `1` to `9` and `0` (where `0` represents speed `10`)
  - stepping backward or forward, respectively with `left arrow key` and `right arrow key` (don't hold down the key!)
  - resuming or starting the simulation with `spacebar`
  - restarting the simulation with `r`
- `Ended`: in this state it's possible to either restarting the simulation with `r` or moving the tape left or right with `left arrow key` and `right arrow key`

You can quit the simulator at any moment with `q` (only with `--keyboard | -k` selected) or `Ctrl+C`

## Import the module
You can also use this simulator by importing it as a module in your python code. This allows your code to interact and control the simulated machine. 

Here's some examples of the thing you can do with it:

```python
import TM_simulator as tm

filename = "bin-dec.txt"
start_tape = "101010"
machine = tm.TuringMachine.load_file(filename, start_tape)
machine.step(10)
machine.print_status()
machine.run()
machine.print_status()
```
```terminaloutput
Output:

Steps: 10   State: decrement  Tape: $101011    Status: Paused    Time elapsed: 1 ms
Steps: 710  State: end        Tape: 42         Status: Ended     Time elapsed: 3 ms
```

It's also possible to get different values regarding the simulator at any point during the simulation. To get additional information on this or the other available features check the [documentation](docs.md).

## Simulator syntax
Check out my extensive [guide](syntax.md) on the syntax of this simulator, where you can find all the information you need.

In the [examples](examples) folder you can find some programs I've made, ranging from easy to hard, that you can run on the simulator.