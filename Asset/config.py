import gnupg
import os


if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep


gpg = gnupg.GPG(gnupghome="C:\Users\mahdi\.gnupg")