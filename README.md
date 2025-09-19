# Turing Machine Simulator

A Turing Machine Simulator coded in Python from scratch by me. It uses a terminal interface to show what the machine is doing.

<img width="1538" height="823" alt="turing simulator 2" src="https://github.com/user-attachments/assets/6ee778df-ca1a-4100-8fbe-b5238f3cf35d" />

It shares the rule syntax and a similar interface with Vittorio Gambaletta's simulator ([VittGam/JSTMSimulator](https://github.com/VittGam/JSTMSimulator)), but it adds new features such as:
- Deterministic behaviour check
- Instant simulation
- Breakpoints [WIP]
- Stepping (back and forward) [WIP]

## Run the script
First, install the module running this command:
```
pip install git+https://github.com/ir-trevi/TM-simulator
```
Then you can use this command to run the simulator:
```
tm-simulator [filename <file>] [input <string>] -a
```
- `filename`: the name of the `.txt` program file that contains the tuples
- `input`: the initial state of the machine tape

There are also some optional arguments:
- `--speed | -s <int>`: set the step speed of the simulation, in a range from `1` to `10`, default is `9`
- `--breakpoints | -b`: enable the breakpoints, pausing the simulation when one is encountered [WIP]
- `--instant | -i`: return the final tape when the machine stops, without the interface
- `--auto | -a`: finds the best interface options based on the terminal size
- `--slim`: make the cells in the tape smaller, useful when the terminal window is small
- `--csize <int>`: set the size of the left code panel, measured in characters. It can also be set to `0` and no code will be displayed
- `--tsize <int>`: set the number of cells visible on the tape

Either `--auto | -a` or both `--csize <int>` and `--tsize <int>` need to be included in the command.  
When `--auto | -a` is selected it will overwrite all the other settings (`--csize`, `--tsize`, `--slim`) except when `--csize` is `0` to disable code.

When `--instant | -i` is selected, all the other interface-related setting will be discarded.

## Simulator syntax
Check my extensive [guide](syntax.md) on the syntax of this simulator, where you can find all the information you need.

In the [examples](examples) folder you can find some programs I've made, ranging from easy to hard, that you can run on the simulator.