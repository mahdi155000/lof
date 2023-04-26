#       IN THE NAME OF GOD
# from Asset import backend
from Asset.backend import *
import termcolor2, pyfiglet

plugins_list = ['add', 'remove', 'rename', 'revalue', 'reid', 'update', 'show']
M_L = []


def save_data(value_, file="LOF.py"):
    with open(PATH + file, 'w') as f:
        f.write("M_L = " + str(value_))
        f.close()


def fill_list(loff):
    for work in loff:
        M_L.insert(100000, work)


def add():
    add_title = input("Enter Title: ")
    add_value = input("Input Value: ")
    add_constant = input("Enter Constant: ")
    add_comment = input("If you want, enter comment: ")
    insert(add_title, add_value, add_constant, add_comment)


def remove():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to delete: ")) - 1
    items = M_L[item_you_want_to_delete]
    delete(items[0])


def rename():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_delete]
    x_item = input(f"Enter new {termcolor2.colored('number', 'yellow')}: ")
    update(items[0], x_item, items[2], items[3], items[4])


def revalue():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_delete]
    x_item = input(f"Enter new {termcolor2.colored('value', 'yellow')}: ")
    update(items[0], items[1], x_item, items[3], items[4])


def reid():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_delete]
    x_value = input(f"Enter new {termcolor2.colored('reid', 'yellow')}: ")
    update_id(items, 0)
    update_id(x_value, items)
    update_id(0, x_value)


def update():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_delete]
    updated_title = input("Enter new title: ")
    updated_value = input("Enter new value: ")
    updated_constant = input("Enter new constant: ")
    updated_comment = input("Enter new comment: ")
    if updated_title == '':
        updated_title = items[1]
        print(items[1])
    elif updated_value == '':
        updated_title = items[2]
        print(items[2])
    elif updated_constant == '':
        updated_title = items[3]
        print(items[3])
    elif updated_comment == '':
        updated_title = items[4]
        print(items[4])
    update(items[0], updated_title, updated_value, updated_constant, updated_comment)


def show():
    items = M_L[0]
    print(items[1], items[2], items[3], items[4])


fill_list(view())
