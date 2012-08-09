"""
This is used for dynamic object completion.
Jedi tries to guess the types with a backtracking approach.
"""
def func(a):
    #? int() str()
    return a

#? int()
func(1)

func

int(1) + (int(2))+ func('')

# Again the same function, but with another call.
def func(a):
    #? float()
    return a

func(1.0)

# Again the same function, but with no call.
def func(a):
    #? 
    return a


# -----------------
# *args, **args
# -----------------
def arg(*args):
    #? tuple()
    args
    #? int()
    args[0]

arg(1,"")
# -----------------
# decorators
# -----------------
def def_func(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

@def_func
def func(c):
    #? str()
    return c

#? str()
func("str")

@def_func
def func(c=1):
    #? int() float()
    return c

func(1.0)

# -----------------
# classes
# -----------------

class A():
    def __init__(self, a):
        #? str()
        a

A("s")

class A():
    def __init__(self, a):
        #? int()
        a
        self.a = a

    def test(self, a):
        #? float()
        a

    def test2(self):
        ##? int()
        self.a

A(3).test(2.0)
A(3).test2()

# -----------------
# list.append/insert
# -----------------
arr = []
for a in [1,2]:
    arr.append(a);

arr.append  # should not cause an exception

#? int()
arr[10]

arr = [tuple()]
for a in [1,2]:
    arr.append(a);

#? int() tuple()
arr[10]
#? int()
arr[10].index()

arr = [""]
arr.insert(0, 1.0)
#? float() str()
arr[10]


# -----------------
# set.append
# -----------------
