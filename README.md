# Turing Machine Simulator

A Turing Machine Simulator coded in Python from scratch by me. It uses a terminal interface to show what the machine is doing.

<img width="1538" height="823" alt="turing simulator 2" src="https://github.com/user-attachments/assets/6ee778df-ca1a-4100-8fbe-b5238f3cf35d" />

It shares the rule syntax with Vittorio Gambaletta's simulator ([VittGam/JSTMSimulator](https://github.com/VittGam/JSTMSimulator)), but it adds new features such as:
- Breakpoints [WIP]
- Stepping (back and forward) [WIP]
- Instant simulation [WIP]

## Run the script
```
python tm-simulator.py [filename] [input]
```
There are also some optional arguments:
- `--speed | -s <int>`: set the step speed of the simulation, in a range from 1 to 10
- `--breakpoints | -b`: enable the breakpoints, pausing the simulation when one is encountered [WIP]
- `--instant | -i`: return the final tape when the machine stops, without the interface
- `--slim`: make the cells in the tape smaller, useful when the terminal window is small
- `--csize <int>`: set the size of the left code panel, measured in characters
- `--tsize <int>`: set the number of cells visible on the tape

## Simulator syntax
Check my extensive [guide](syntax.md) on the syntax of this simulator, where you can find all the information you need.
