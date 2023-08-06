##clicolors - Command Line Interface::Colors
###Simply Python module to colorize your Linux terminal. 

Usage:
```python
from clicolors import colorize

# example 1
print colorize('Example text 1', fg='blue',bg='red',attr='bold')
```
![alt text][1]

```python
# example 2
print colorize('Example text 2', 'blue','red','bold')
```
![alt text][2]

```python
# example 3
print colorize('Example text 3', fg='yellow')
```
![alt text][3]

```python
# example 4
print colorize('Example text 4', 'yellow')
```
![alt text][4]

```python
# example 5
print colorize('Example text 5', bg='green')
```
![alt text][5]

```python
# example 6
print colorize('Example text 6',attr='underline')
```
![alt text][6]

```python
# example 7
print colorize('Example text 6',bg='cyan',attr='underline',fg='black')
```
![alt text][7]

```python
# clicolors Demo
from clicolors import colorize, COLORS, ATTRIBUTES

print colorize('clicolors : Lightweight Python script for styling strings in your Linux terminal',fg='black',bg='white',attr='underline')
print ('Foreground: '+' '.join([colorize(color, fg=color) for color in COLORS]))
print ('Background: '+' '.join([colorize(color, bg=color) for color in COLORS]))
print ('Attributes: '+' '.join([colorize(attributes, attr=attributes) for attributes in ATTRIBUTES]))
```
![alt text][8]

[1]: /images/example1.jpg "Example Text 1"
[2]: /images/example2.jpg "Example Text 2"
[3]: /images/example3.jpg "Example Text 3"
[4]: /images/example4.jpg "Example Text 4"
[5]: /images/example5.jpg "Example Text 5"
[6]: /images/example6.jpg "Example Text 6"
[7]: /images/example7.jpg "Example Text 7"
[8]: /images/clicolorsDemo.jpg "clicolors Demo"
