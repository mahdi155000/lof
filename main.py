#                       IN THE NAME OF GOD
import os
from Asset import plugins
from Asset import backend
import termcolor2, pyfiglet

print(termcolor2.colored(pyfiglet.figlet_format("IN THE NAME OF GOD"), 'red'))


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
        if l <= os_tab_number:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t\t\t"{work[2]}'
            # text = str(num) + f') For {do_what} one ' + f'"{work[1]}":\t\t\t\t\t"{work[2]}"'
        elif l <= os_tab_number * 2:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t\t"{work[2]}'
        elif l <= os_tab_number * 3:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t\t"{work[2]}'
        elif l <= os_tab_number * 4:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t\t"{work[2]}'
        elif l <= os_tab_number * 5:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": \t"{work[2]}'
        elif l > os_tab_number * 5:
            text = str(num) + f') for  {do_what} one ' + f'"{work[1]}": "{work[2]}'
        print(termcolor2.colored(text, color))


# M_L = [[1, "test", 15], [2, "are you OK", 52]]

M_L = []

fill_list(backend.view())
print("---------------------------------------------")
print(M_L)
print("---------------------------------------------")
print("Please enter your number:\n0) add\\minus\\set manually")
work_counter = 1
# for work in M_L:
#     print(f"{work_counter}) {work[1]}")
#     work_counter += 1
show_item("plus")
# print("enter 'c' for go to command mode.")

while True:
    what_to_do = input("->:\n").lower()
    try:
        if type(int(what_to_do)) == int:
            try:
                lNumber = int(what_to_do)
                if lNumber >= 0:
                    addNumber = 1
                    li = M_L[lNumber - 1][2]
                    M_L[lNumber - 1][2] += 1
                elif lNumber < 0:
                    lNumber = abs(lNumber)
                    addNumber = -1
                    li = M_L[lNumber - 1][2]
                    M_L[lNumber - 1][2] -= 1
                print(M_L[lNumber - 1])
            except:
                print("Your input number not in range")
    except:
        pass
    if what_to_do == 'q' or what_to_do == '':
        exit(0)
    # elif what_to_do in plugins.plugins_list:
    elif hasattr(plugins, what_to_do) and callable(getattr(plugins, what_to_do)):
        getattr(plugins, what_to_do)()
        # plugins.locals()
        # locals()[what_to_do]()
    elif what_to_do == "show item":
        show_item()
    else:
        print("Your command is not supported")
