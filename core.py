import requests
import json
from jsondiff import diff


with open("webhookResponse.json") as wr:
    webhookResponse = json.load(wr)

with open("database.json") as db:
    database = json.load(db)

def loadConfig():
    with open("config.json", "r") as cfg:
        data = json.load(cfg) 
        API_KEY = data["API_KEY"]
        TOKEN = data["TOKEN"]
        CALLBACKURL = data["CALLBACKURL"]
    return API_KEY, TOKEN, CALLBACKURL

API_KEY, TOKEN, CALLBACKURL = loadConfig()


ID = "6760b2c95e76947778ce0dac"


BASEURL = "https://api.trello.com/1/"


def getCard(cardID):
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        BASEURL + "cards/{}".format(cardID),
        headers=headers,
        params=query
    )

    print(response.json())
    return response.json()


def getBoards():
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        BASEURL + "members/me/boards?key={}&token={}".format(API_KEY, TOKEN),
        headers=headers,
        params=query
    )

    # Filter out the deleted/unactive boards so only active ones get returned
    activeBoards = [x for x in response.json() if x["closed"] == False]

    return activeBoards



def getFilteredListsOnBoard(boardID, filter="open"):
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        BASEURL + "boards/{}/lists/{}?key={}&token={}".format(boardID, filter, API_KEY, TOKEN, ),
        headers=headers,
        params=query
    )

    return response.json()

def createMirrorCard(listID, idCardSource):
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "POST",
        BASEURL + "cards?key={}&token={}&idList={}&idCardSource={}&keepFromSource=all".format(API_KEY, TOKEN, listID, idCardSource),
        headers=headers,
        params=query
    )

    return response.json()

def checkDifferences():
    """
    Returns differences between newly updated card and the outdated mirrored card which needs to receive update.
    """
    updatedModel = webhookResponse["model"]

    # find already mirrored cards for this card
    if updatedModel["id"] in database:
        mirroredCardID = database[updatedModel["id"]]
        mirroredCardModel = getCard(mirroredCardID)

        difference = diff(mirroredCardModel, updatedModel)
        updateCard(mirroredCardID, desc="this is new desc", name="this is new name")

    return



def updateCard(id, name=None, desc=None, closed=None, idMembers=None, idAttachmentCover=None, idList=None, idLabels=None,
               idBoard=None, pos=None, due=None, start=None, dueComplete=None, subscribed=None, address=None,
               locationName=None, coordinates=None, cover=None):
    """
    Updates the card with the given ID.
    """
    params = locals()
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN,
    }
    # works for now, it just takes all parameters and adds them to the query
    query.update(params)

    response = requests.request(
        "PUT",
        BASEURL + "cards/{}".format(id),
        headers=headers,
        params=query
    )
    print("Card updated!")
    #print(response.json())
    return response.json()


def createWebhook(cardID):
    url = "https://api.trello.com/1/webhooks/"

    headers = {
        "Accept": "application/json"
    }

    query = {
        'callbackURL': CALLBACKURL,
        'idModel': cardID,
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )

    return response.json()


def updateCardAction(webhookRequest):
    data = webhookRequest["action"]["data"]

    changedProperty = list(data["old"].keys())[0]

    # find all associated cards to be updated
    cardID = database[webhookRequest["model"]["id"]]

    match changedProperty:
        case "name":
            updateCard(cardID, name=data["card"][changedProperty])

        case "desc":
            updateCard(cardID, desc=data["card"][changedProperty])

        case "closed":
            updateCard(cardID, closed=str(data["card"][changedProperty]).lower())

        case "idMembers":
            updateCard(cardID)
        case "idAttachmentCover":
            updateCard(cardID)
        case "idList":
            updateCard(cardID)
        case "idLabels":
            updateCard(cardID)
        case "idBoard":
            updateCard(cardID)
        case "pos":
            updateCard(cardID)
        case "due":
            updateCard(cardID)
        case "start":
            updateCard(cardID)
        case "dueComplete":
            updateCard(cardID)
        case "subscribed":
            updateCard(cardID)
        case "address":
            updateCard(cardID)
        case "locationName":
            updateCard(cardID)
        case "coordinates":
            updateCard(cardID)
        case "cover":
            updateCard(cardID)
        case _:
            print()
    return