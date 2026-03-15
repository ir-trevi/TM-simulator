# Simulator module documentation
This module is just a wrapper of the already existing structure originally meant to only be run as a script. 
The only difference is that this module was made to be able to interact with the simulation with code; one example of this may be a solution checker script that checks each different possible solution (if the domain of the solution is limited).

## Module structure
The module structure is quite simple as it is composed by two parsing functions, `parse_tuples` and `parse_breakpoints`, that handles the parsing of the tuples and the `TuringMachine` class, the one that handles the simulated turing machine. 
Inside this class there are various methods and variables, as described in the following paragraphs.

## Parsing functions
In the module there are two different parsing functions, `parse_tuples` and `parse_breakpoints` that convert the input tuples in a way the machine can handle.
They have the same input and output format, with the only difference being the contents of it. 

The length of the returned list is different from the number of lines in the input file because the parsing process expands all the notations in the tuples into single base tuples, increasing the total amount of tuples.

I chose to build a machine based on parsed tuples in the base form with no notations, unpacking all the tuples. In this way the time spent searching for the correct tuple instead is lower compared to the interpretation of all the notation at each search.   

### Tuple parsing
```python
parse_tuples(input_string: str, is_file: bool = True, to_print: bool = False) -> list[TuringTuple]
```
This function takes `input_string` as an input that can either be the name of the file to parse (usually a `.txt`) or a string containing the tuples. This selection is done with the `is_file` boolean argument, set to `True` by default because passing a filename is the preferred method.

The other argument, `to_print`, can be used to convert the `TuringTuple` objects in the list to their string representation that can be visualized or printed more easily.

### Breakpoint parsing
```python
parse_breakpoints(input_string: str, is_file: bool = True) -> list[bool]
```
This function, similarly to the previous one, parses the `input_string` with the `is_file` boolean argument, accepting both a filename or a string representation of the tuples, and returning a list of boolean values where `True` represents a breakpoint.

## Machine class
The `TuringMachine` class is simply a more user-friendly wrapper of the basic class in this module that is used in the command line script, with some functions to control its simulation.

By default the machine is always paused, running only when the `step` or `run` function is called and, while paused, its values can be accessed and modified. 

### Loading the input
```python
TuringMachine.load_file(filename: str, input_tape: str) -> TuringMachine
TuringMachine.load_tuples(parsed_tuples: list[TuringTuple], parsed_breakpoint: list[bool], input_tape: str) -> TuringMachine
```
When initialising the machine you need to load the tuples and to do that there are two ways: one of them is using the name of the file to parse and the other one is to pass the two parsed lists of tuples and breakpoints.

With the `load_file` initialiser you pass the `filename` of the file to be parsed (it's preferred to use r strings to avoid creating problems with backslashes) along the initial state of the `input_tape`.

With the `load_tuples` initialiser you need two lists containing the `parsed_tuples` and the `parsed_breakpoints`, that can be obtained using the two parsing functions listed before. Just like the previous initialiser you need to also pass the `input_tape`.

### Running the machine
```python
run() -> None
```
This function takes no input as it runs the machine indefinitely until the machine halts (or the threshold is reached, see the `set_threshold` function to more information).

### Stepping the machine
```python
step(times: int = 1) -> None
```
This function steps the machine forward as many times as indicated in the `times` argument. Unlike the `run` function, it ignores the set threshold, stepping for the indicated amount of times.

There is also the `step_back` function that, as the name says, steps the machine back.
```python
step_back(times: int = 1) -> None
```
This function has the same argument as the previous one but it works differently: since stepping back in a turing machine is not possible, the only way to accomplish the result is to run from the start the machine again stopping at the selected step.

### Setting the breakpoints
```python
set_breakpoints(value: bool = True) -> None
```
This helper functions simply enables or disables the breakpoints from pausing the code. The default `value` is `True` because the machine starts the simulation with the breakpoints disabled.

### Setting the threshold
```python
set_threshold(value: int) -> None
```
This helper functions set the maximum steps the `run` function will perform before stopping to the `value`. This is done to avoid the case where the machine gets in an infinite loop, exiting it; the default threshold value of the machine is 500.000 steps. 
Each time the `run` function is called, the amount of steps performed in the function is set to 0 at each function call.

### Print the status
```python
print_status() -> None
```
This function prints most the most important variables to understand what's the machine is doing, these are the number of steps since the beginning of the simulation, the name of the state the machine is, the whole tape and the state of the simulation.

This is the typical output of this function:
```terminaloutput
Steps: 10    State: decrement    Tape: $101011    Status: Paused    Time elapsed: 1 ms
```

### Variables
The variables of the machine that can be accessed during the simulation are:
- `state: str`: the name of the state the machine is in
- `tape: list[str]`: the used part of the tape as a list of the content of the single cells
- `steps: int`: the number of elapsed steps since the beginning if the simulation
- `runtime: float`: the number of seconds, rounded to the milliseconds, the machine has taken that far to run the simulation
- `ended: bool`: whether the machine has halted the simulation
- `paused: bool`: whether the machine is in the paused state 