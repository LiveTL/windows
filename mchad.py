import requests

MCHAD = 'https://repo.mchatx.org'

def getRoomList():
    return requests.get(f'{MCHAD}/Room/').json()

def getRoom(id, idonly = True):
    if idonly:
        id += 'YT_'
    return requests.get(f'{MCHAD}/Room/?link={id}').json()

if __name__ == "__main__":
    print('mchad test')
    print(getRoomList())
    print(getRoom('mJwpVT1WvLg'))