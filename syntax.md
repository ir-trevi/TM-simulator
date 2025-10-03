## Rule syntax
The basic code unit in the machine is represented by a tuple made of 5 elements separated by comma and enclosed by brackets as it follows:  
```
(current state, current symbol, new state, new symbol, movement)
```
`Current state`: the state in which the machine needs to be, the machine starts with the state `0`  
`Current symbol`: the symbol on tape which the head needs to read, each tape cell contains `-` by default    
`New state`: the state the machine transitions to when both `Current state` and `Current symbol` are verified  
`New symbol`: the symbol written on the cell at the tape head when both `Current state` and `Current symbol` are verified  
`Movement`: the direction the machine will move when both `Current state` and `Current symbol` are verified, it can be either `>` (right movement), `<` (left movement) or `-` (no movement)  

Take this tuple as an example:
```
(move1, -, move2, ., >)
```  
It follows this logic: if the machine is in the state `move1` and the head reads the symbol `-`, set the machine state as `move2` and overwrite the symbol with `.`, then move the tape to the right (`>`)  

Since the machine follows a specific order to check the tuples, having two tuples with the same `Current state` and `Current symbol` but different `New state`, `New symbol` or `Movement` will lead to a behaviour based on the position of the tuples in the code. This is what's called a non-deterministic scenario because the machine should give the same output no matter what the order of the tuples in the code are.

On the other hand duplicate tuples are allowed, but it's recommended to just keep a single copy of each tuple in the code even if the result is still deterministic.

### Comments
Comments can be added after a tuple or by themselves on an empty line and are preceded by a hash sign `#`.

Here's an example:
```
(remove, a, remove, -, >)   # this is a comment
# this is also a comment 
``` 

### Breakpoints
Breakpoints are used to stop the simulation when a specific tuple with is the one with the matching `Current state` and `Current symbol` of the machine. It's marked by an exclamation mark `!` just before the opening bracket `(`, so with these tuples:
```
!(find_a, a, found, -, -)
(find_b, b, found, -, -)
(find_c, c, found, -, -)
```  
The simulation will be paused whenever the machine `current state` is `find_a` and the `current symbol` is `a`.

### Special characters
Some characters cannot be use directly neither as symbols nor as characters in the state name. These characters are the ones needed for the syntax and therefore needs to be escaped with `\ ` to be considered valid. Those are:
- All the brackets `(`, `)`, `[`, `]`, `{`, `}`
- Comma `,`
- Hash sign `#`
- Circumflex `^`
- Hyphen `-` (without escaping it represents an empty space on the tape)
- The backslash itself `\ `

### Multiple symbols notation
It is possible to use multiple symbols in the `Current symbol` or `New symbol` element to compress multiple similar tuples into one. This is possible because those two elements are not limited to a single symbol, instead they can accept multiple symbols.

With this notation, these 6 tuples that share `Current state` and `New state`:
```
(check, 1, move, 1, <)
(check, 2, move, 2, <)
(check, 3, move, 3, <)
(check, 4, move, 4, <)
(check, 5, move, 5, <)
(check, 6, move, 6, <)
```  
Could be represented with this one tuple:
```
(check, 123456, move, 123456, <)
``` 
This doesn't imply that the two sets of symbols needs to be identical because when expanding the tuple, the first `Current symbol` is matched with the first `New symbol` and so on.  

The only limitation is that they both need to have the same number of symbols or `New symbol` has only 1 symbol (and not the other way around, otherwise the machine wil be non-deterministic).

Here's an example using different symbols sets:
```
(add, 123, return, abc, <)
```
```
(add, 1, return, a, <)
(add, 2, return, b, <)
(add, 3, return, c, <)
```

And here's an example using symbol sets with different length:
```
(check, wxyz, move, -, >)
```
```
(check, w, move, -, >)
(check, x, move, -, >)
(check, y, move, -, >)
(check, z, move, -, >)
```
With this notation it's also possible to have multiple symbols in the `Movement` element, but it's not recommended as it can easily lead to non-deterministic behaviours.

Since `Current state` and `New state` are considered strings, they cannot be expanded in this way. A different way to accomplish this is using classes (check the class paragraph).

### Double dot notation
In addition to the multiple symbols notation, you can use the double dot notation to make the symbol set of `Current symbol` or `New symbol` more compressed.
It's marked by 2 characters separated by a double dot `..` and it expands to the set of all characters between them, both included.

With this notation, the example shown in the previous paragraph:
```
(check, 1, move, 1, <)
(check, 2, move, 2, <)
(check, 3, move, 3, <)
(check, 4, move, 4, <)
(check, 5, move, 5, <)
(check, 6, move, 6, <)
```  
```
(check, 123456, move, 123456, <)
```  
Can become even more compressed:
```
(check, 1..6, move, 1..6, <)
``` 
It's also possible to concatenate multiple double dot notation one after another or append letters before and after. In this way these tuples:
```
(skip, -, skip, -, <)
(skip, abcdef, skip, abcdef, <)
(skip, 012345, skip, 012345, <)
```  
Can be written as this single tuple:
```
(skip, -a..f0..5, move, -a..f0..5, <)
```
Obviously numbers and letters cannot be mixed up with this notation as the two characters needs to be of the same type and in ascending order (numerical or alphabetical). Anything else that is neither a letter nor a number is invalid.

Just like the previous one, this method cannot be applied to `Current state` and `New state` as they would interpret it as a string and not as a set of symbols.

### Exclusion notation
This notation, just like the previous two, can reduce the size of the symbol set of `Current symbol` or `New symbol`. It's represented by a circumflex `^` and it represents all the symbols except the ones after it.

Take this tuple with exclusion notation as an example:
```
(delete, ^abc, delete, -, <)
``` 
It will be expanded to this tuple (where `*` represents all the special characters):
```
(delete, defghijklmnopqrstuvwxyz0123456789*, delete, -, <)
```
Unlike the double dot notation that can be combined with others symbols, the exclusion notation needs to be used without any symbols before the `^`. 

When using this notation it's highly recommended to use the same set of excluded symbols on both `Current symbol` or `New symbol` to avoid unexpected (but deterministic) behaviours or use it only on `Current symbol` with a single symbol for `New symbol`.

### Class notation
This notation is the most powerful as it's the only one that allows the creation of a set with different symbols that can be interpreted as `Current state` or `New state`, as well as all the other tuple elements. 

There are two types of classes identified by this two types of brackets, independent of each other:
- Square brackets `[]`
- Curly brackets `{}`

Using classes, these tuples:
```
(search, 0, read_0, 0, >)
(search, 1, read_1, 1, >)
(search, 2, read_2, 2, >)
(search, 3, read_3, 3, >)
(search, 4, read_4, 4, >)
```
Are equivalent to these two (even if the use of the square bracket is preferred over curly ones):
```
(search, [01234], read_[01234], [01234], >)
```

```
(search, {01234}, read_{01234}, {01234}, >)
```

They work in a similar way as the multiple symbols notation, where the tuples are made matching the first element in each class, the second in each class and so on. Classes also supports all the notations described above like the exclusion and the double dot notation.

This means that the symbols set in each class can be different as long as they have the same amount of symbols. Classes with a single symbol are syntactically correct, but if it's preferred to move them out of the class, like in this example:
```
(0, [0..9], read_[0..9], [-], >)
```
```
(0, [0..9], read_[0..9], -, >)
```

It's even possible to use both types of classes in a single tuple (or a class type and multiple symbols in `Current symbol` or `New symbol`) but the way it expands is much different. 

Take this tuple as an example:
```
(move_[a..z], {0..9}, move_[a..z], {0..9}, <)
```
It will be expanded in every possible combination of the class symbol and `Current symbol`/`New symbol`. So the expansion will result in these tuples:
```
(move_a, 0, move_a, 0, <)
(move_a, 1, move_a, 1, <)
...
(move_a, 9, move_a, 9, <)
(move_b, 0, move_b, 0, <)
(move_b, 1, move_b, 1, <)
...
(move_b, 9, move_b, 9, <)
...
...
(move_z, 0, move_z, 0, <)
(move_z, 1, move_z, 1, <)
...
(move_z, 9, move_z, 9, <)
```


