#       IN THE NAME OF GOD
# from Asset import backend
from Asset import backend
import termcolor2

plugins_list = ['add', 'remove', 'rename', 'revalue', 'reid', 'update', 'show', 'sort']
M_L = []


# def save_data(value_, file="LOF.py"):
#     with open(PATH + file, 'w') as f:
#         f.write("M_L = " + str(value_))
#         f.close()
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)


def add():
    add_title = input("Enter Title: ")
    add_value = input("Input Value: ")
    try:
        if type(int(add_value)) is int:
            add_value = int(add_value)
    except:
        pass
    add_constant = input("Enter Constant: ")
    add_comment = input("If you want, enter comment: ")
    backend.insert(add_title, add_value, add_constant, add_comment)


def remove():
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to delete: ")) - 1
    items = M_L[item_you_want_to_delete]
    backend.delete(items[0])


def rename():
    item_you_want_to_rename = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_rename]
    x_item = input(f"Enter new {termcolor2.colored('number', 'yellow')}: ")
    backend.update(items[0], x_item, items[2], items[3], items[4])


def revalue():
    item_you_want_to_revalue = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_revalue]
    x_item = input(f"Enter new {termcolor2.colored('value', 'yellow')}: ")
    backend.update(items[0], items[1], x_item, items[3], items[4])


def reid():
    item_you_want_to_reid = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_reid][0]
    x_value = input(f"Enter new {termcolor2.colored('reid', 'yellow')}: ")
    backend.update_id(items, 0)
    backend.update_id(x_value, items)
    backend.update_id(0, x_value)


def update():
    item_you_want_to_update = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_update]
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
    backend.update(items[0], updated_title, updated_value, updated_constant, updated_comment)


def show():
    for work in M_L:
        print(work[1], work[2])


def help():
    print("You can use this function: ")
    for i in plugins_list:
        print("->" + i)


def sort():
    counter = 1
    for item in M_L:
        # backend.update(counter, item[1], item[2], item[3], item[4])
        backend.update_id(item[0], counter)
        # item[0] = counter
        counter += 1

M_L=[]
fill_list(backend.view())
