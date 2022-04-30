import math


def func_test():
    sum = 0
    for i in range(10):
        sum += 1
    return sum


def example_butoma():
    return math.ceil(math.sin(math.radians(30)))


class Example:

    def __init__(self):
        self.fruit = "Apple"
        self.name = "Jack"
        self.sex = "helecopter"
        self.answer = True
        self.probobility = False
        self.list = ["Egor", "Kiril", "j", 1, "ALARM", 12]
        self.bytes = b'\xd0\x91\xd0\xb0\xd0\xb9\xd1\x82\xd1\x8b'

    def calculate(self):
        return 1 + 1


class Student:

    def __init__(self):
        self.fruit = "Apple"


def decorater(fun):
    obj = Example()
    cur_dict = {'1': 1, '2': 2}
    test_type = Student

    def wrapped(*arg, **kwargs):

        if len(kwargs) != 0:
            print(fun(arg[0], kwargs['t']))
            obj.calculate()
            print(cur_dict)
            print(test_type)

        else:
            print(fun(arg[0]))

    return wrapped


l = 6
global_list = [1, 2, 3]
global_dict = {'1': 1, '2': 2}
global_object = Example()


@decorater
def print_hi(name, t=True):
    current_obj = global_object
    student = Student()
    my_list = global_list
    my_dict = global_dict
    error_dict = {"1": "apple", "2": "orange"}
    x = 15
    g = 13 + l

    if t:
        print_hi("Jack", t=False)

    test_list = (x, g)
    print(f'Hi, {name}')

    return math.sin(9)


class Test:
    argument = "NaSvyzi"
    beta = Example()

    def __init__(self):
        self.empty_str = ""
        self.empty_list = []
        self.empty_dict = {}
        print("All right")
        self.fraction = -0.00000001201212
        print_hi("Man")
        self.empty = None
        self.age = 18
        self.answer = True
        self.name = "Jack"
        self.sex = "man"
        self.list = ["ada", 213, True, {"Axe": 1, "Atacks": 2}]
        self.my_dict = {"Street": "A.Bachilo"}

    def stick_finger(self):
        print("Good morning")

    @staticmethod
    def jump():
        print("Static is ready")
        return "All right"

    @classmethod
    def pussy(cls):
        print(f"I am here{cls.argument}")
