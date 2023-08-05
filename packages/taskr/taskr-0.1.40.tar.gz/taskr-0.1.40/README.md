# Taskr

## Installation

via pip:

```
pip install taskr
```



## Usage - Task


### ```@task``` decorator

Setup a task function like (Let's call it as "utils.py")

```
from taskr import task

@task
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
   
if __name__ == '__main__':
    task.dispatch()
```

Then execute by

```
$ python utils.py run Tokyo Yokohama
```

And you'll get

```
Run from Tokyo to Yokohama by speed=42
```

To get help of utils.py

```
$ python utils.py run -h
usage: utils.py run [-h] [--speed SPEED] source destination

positional arguments:
  source
  destination

optional arguments:
  -h, --help     show this help message and exit
  --speed SPEED
```


### ```@task.set_name``` decorator

By default, we make the name of the function as its action/task name.
If you want to change the action name, you can use ```@task.set_name``` decorator like this

```
@task
@task.set_name('run_to')
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
```

And now execute by

```
$ python utils.py run_to Tokyo Yokohama
```


### ```@task.set_argument``` decorator

taskr uses ```argparse``` module of Python to parse argument passed in.
By default, we map positional argument of task function into required positonal argument of argparser and
optional argument of task function into optional argument of argparser.

If you want to change this behavior or add help text, choice limitation, and etc when setup argparse,
you can use ```@task.set_argument``` decorator and pass the same arguments you pass when using argparse.

```
@task
@task.set_argument('source', help='The source where you come from', choice=('Tokyo', 'Osaka'))
@task.set_argument('--speed', '-s', help='The speed you wanna run', type=int, dest='speed')
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
```

And now you can only run from Tokyo or Osaka but cannot run from Kyoto
Also you must run in an int value speed.

For positional arguments, taskr matches its name and argument of function automatically.
But for optional arguments, you must assign ```dest``` to make taskr understand which argument of function
shoule map to.


### ```@task.pass_argparse_namespace``` decorator

If your task function has set ```pass_argparse_namespace``` by this decorator,
then all the argument of argparse should be decalred explicitly. (i.e. taskr won't discover for you automatically)
Also the argument passed into your task function is only the "Namespace" comes from argparse

For example

```
@task
@task.pass_argparse_namespace
@task.set_argument('start_time')
@task.set_argument('end_time')
def sleep(arguments):
    print('Sleep from {0.start_time} to {0.end_time}'.format(arguments))
```


## Usage - console & Color

The ```console``` helps you to print color message on console.

It gives you a str 'Hello World' with loght red color and white background.
Also you can use ```console.info```, ```console.error```, ```console.success```, ```console.highlight```,
and ```console.prompt``` to print messages

To get colored string, use Color.str.

```
Color.str('Hello World', foreground=Color.RED, background=Color.White, light=True)
```

It gives a 'Hello World' string with light red text and white background.
