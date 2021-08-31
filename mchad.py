import requests

MCHAD = 'https://repo.mchatx.org'

def getRoom(id):
    print(requests.get(MCHAD + '/Room/?link=YT_' + id).json())
