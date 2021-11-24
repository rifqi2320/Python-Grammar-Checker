# Python Grammar Checker

## General Information

> This project is a syntax checker module for Python programming language that is developed for second major assignment of IF2124 Theory of Formal Language and Automata.

## Table of Contents

- [Python Grammar Checker](#python-grammar-checker)
  - [General Information](#general-information)
  - [Table of Contents](#table-of-contens)
  - [Features](#features)
  - [Directory Structure](#directory-structure)
  - [Setup](#setup)
    - [Setting up the environment](#setting-up-the-environment)
    - [Installing the module](#installing-the-module)
  - [Usage](#usage)
  - [Screenshots](#screenshots)
  - [Room for Improvements](#room-for-improvements)
  - [References](#references)
  - [Developed by](#developed-by)

## Features

- Checking the grammar of your code! (and showing what's wrong)
- Accessible as a module and as a program
- Custom Keyword and grammar
- Verbose option
- Indentation check option

## Directory Structure

The project directory structure depicted with this tree

```
└──tbfo
   ├───examples
   │   ├───python.cfg
   │   └───tokens.txt
   ├───parser
   │   ├───cyk.py
   │   └───fa.py
   ├───grammar.py
   └───lexer.py

```

## Setup

### Setting up the environment

We recommend using virtual environment (venv) on installing the package.

```
pip install venv
```

Then, initialize the virtual environment using

```
venv
```

### Installing the module

On the main directory folder install the module using pip by running the command

```
pip install -e .
```

And you're good to go ;)

## Usage

There are two ways on accessing the module

1. Using the module on your python script

```py
from tbfo import *
```

2. Using the main program on the module

```
py -m tbfo {Your_python_script.py} {args}
```

### List of Args

- Verbose (-v)
- No Indentation (-ni)

## Screenshots

## Room for Improvements

Because of the time constraints of the assignment, we skipped some values on the grammar checker like:

- Async/Await function
- Multiline continuation parenthesis
- Multiline strings

## Reference

- [The Python Language Reference for Python 3.6](https://docs.python.org/3.6/reference/)
- [Teori Finite State Automata](https://media.neliti.com/media/publications/226255-telaah-teoritis-finite-state-automata-de-8b056b07.pdf)
- [CYK Parsing over Distributed Representations](https://www.mdpi.com/1999-4893/13/10/262/htm)

## Developed by

- Rifqi Naufal Abdjul / 13520062
- Saul Sayers / 13520094
- Amar Fadil / 13520103
