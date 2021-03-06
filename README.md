# Calculator

## Basic Usage

Just like using Python REPL, you can simply type in some calculations:

```
==> 1 + 1
Œ >-> 2
==> 2 ^ 10
Œ >-> 1024.0
```

Symbol Œ represents "Output of Evaluation"(:P), and it cannot be manipulated. 

Also, you can define some variables:

```
==> a=10.0
==> b=6
==> a+b
Œ >-> 16.0
```

Very Easy. 

Borrowing a feature of Python, the value assignment above can be done in one line:

```
==> a, b = 10, 6
==> a * b
Œ >-> 60.0
```

If you no longer need a variable, you can use keyword `rm` to delete the instance:

```
==> a = 10
==> a
Œ >-> 10.0
==> rm a
==> a
NameError: a is not defined
```

Also, for your convenience, you can assign a value to a variable named `rm`. This action will not influence the effect of command `rm`, since the command and variable instance are separately stored. 

## Math Library

### Math Functions

To simplify calculation efforts for users, the calculator carries math functions that are supported by Python. You can use the command `\math_func` to list out all functions in this script. 

```
==> sqrt(2)
Œ >-> 1.4142135623730951 
```

For your convenience, if there is only one parameter passed in the function, you can omit the parenthesis:

```
==> sqrt 2
Œ >-> 1.4142135623730951 
```

**However, if you call functions continuously, you can only apply this feature for the last function you call**

```
==> sqrt(sqrt 2)
Œ >-> 1.189207115002721
```

This is done for enhancing the readability of your calculation expressions as well as the simplification of the implementation of the evaluator(XD)

### Math Consts

You can use the command `\math_const` to list all the constants that are built in the calculator:

```
==> e
Œ >-> 2.718281828459045
```

And for respecting people who found those values, you are not allowed to change the values of those constants though you will not receive a warning if you do so(cuz a warning can devastate one's mood while using a software). 

```
==> e=10
==> e
Œ >-> 2.718281828459045
```

## Functions

The syntax of defining a function is:

```
{e1, e2, e3->...}
```

For instance, you can define a function to find out the maximum value among three values:

```
==> someFun = {x,y,z->max(max(x,y),z)}
==> someFun(1,2,3)
Œ >-> 3.0 
```

Also, function can be taken as a parameter:

```
==> someFun = {x,y,z->x(y,z)}
==> someFun({a,b->a^b}, 2, 10)
Œ >-> 1024.0
```

