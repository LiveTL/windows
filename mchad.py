from tkinter.constants import E
import requests

MCHAD = 'https://repo.mchatx.org'

def getRoomList():
    return requests.get(f'{MCHAD}/Room/').json()

def getRoom(id, idonly = True):
    if idonly:
        id = 'YT_' + id
    try:
        return requests.get(f'{MCHAD}/Room/?link={id}').json()[0]
    except IndexError:
        return None

def getRoomByName(name):
    return requests.get(f'{MCHAD}/Room/?name={name}').json()[0]

if __name__ == "__main__":
    print('mchad test')
    print(getRoomList())
    print(getRoom('0BBfB9N_VFs'))
    print(getRoomByName('Translator Vee'))