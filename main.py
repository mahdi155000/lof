#                       IN THE NAME OF GOD
import os
import sqlite3
import os
from Asset import plugins
from Asset import backend
import termcolor2, pyfiglet

if os.name == 'nt':
    os.system('color')
print(termcolor2.colored(pyfiglet.figlet_format("IN THE NAME OF GOD"), 'red'))

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep


def plus(item):
    M_L[item - 1][2] += 1


def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)


def show_item(do_what='plus'):
    num = 0
    for work in M_L:
        num += 1
        if num % 2 == 0:
            color = 'blue'
        else:
            color = 'red'
        l = len(str(work[1]))
        os_tab_number = 6
        # if os.name == 'nt':
        #     os_tab_number = 4
        # print("I change tab number for Windows")
        if l < os_tab_number:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t\t"{work[2]}'
            # text = str(num) + f') For {do_what} one ' + f'"{work[1]}":\t\t\t\t\t"{work[2]}"'
        elif l < os_tab_number * 2:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t\t"{work[2]}'
        elif l < os_tab_number * 3:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t"{work[2]}'
        elif l < os_tab_number * 4:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t"{work[2]}'
        elif l < os_tab_number * 5:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t"{work[2]}'
        elif l > os_tab_number * 5:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": "{work[2]}'
        print(termcolor2.colored(text, color))


def new_show(do_what='plus'):
    id_counter = 1
    for item in M_L:
        if item[0] % 2:
            show_color = 'blue'
        else:
            show_color = 'red'
        if item[0] < 10:
            text = (" {:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        else:
            text = ("{:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        print(termcolor2.colored(text, show_color))
        id_counter += 1


# M_L = [[1, "test", 15], [2, "are you OK", 52]]

M_L = []

fill_list(backend.view())
print("---------------------------------------------")
print(M_L)
print("---------------------------------------------")
# print("{:<3}) {:<50} {:<10}".format('num', 'work', 'value'))
# print("Please enter your number:\n0) add\\minus\\set manually")
work_counter = 1
# for work in M_L:
#     print(f"{work_counter}) {work[1]}")
#     work_counter += 1
# show_item("plus")
new_show()
# print("enter 'c' for go to command mode.")

while True:
    what_to_do = input("->:\n").lower()
    INT_check_var = False
    try:
        if type(int(what_to_do)) == int:
            try:
                lNumber = int(what_to_do)
                if lNumber >= 0:
                    addNumber = 1
                    li = M_L[lNumber - 1]
                    backend.update(li[0], title=li[1], value_=int(li[2]) + addNumber, constant=li[3], comment=li[4])
                    # M_L[lNumber - 1][2] += 1
                elif lNumber < 0:
                    lNumber = abs(lNumber)
                    addNumber = -1
                    li = M_L[lNumber - 1][2]
                    backend.update(li[0], title=li[1], value_=int(li[2]) + addNumber, constant=li[3], comment=li[4])
                    # M_L[lNumber - 1][2] -= 1
                INT_check_var = True
            except Exception as e:
                print("Your input number not in range")
    except Exception as e:
        # print(e)
        pass
    if INT_check_var:
        pass
    elif what_to_do == 'q' or what_to_do == '':
        exit(0)
    # elif what_to_do in plugins.plugins_list:
    elif hasattr(plugins, what_to_do) and callable(getattr(plugins, what_to_do)):
        try:
            getattr(plugins, what_to_do)()
        except Exception as e:
            pass
            # print("I can't run your command.")
            # print(e)

        # plugins.locals()
        # locals()[what_to_do]()
    elif what_to_do == "show item":
        # show_item()
        new_show()
    else:
        print("Your command is not supported")

    try:
        M_L = []
        fill_list(backend.view())
        counter = 1
        for item in M_L:
            backend.update(counter, item[1], item[2], item[3], item[4])

        lNumber = int(what_to_do)
        print(M_L[lNumber - 1])
    except Exception as e:
        print("Operating failed!!!")
        # print(e)
