import hashlib
import uuid

import requests
import json
from datetime import datetime
import time

# database imports
import models
from os import environ

def loadConfig():
    API_KEY = environ.get("API_KEY")
    TOKEN = environ.get("TOKEN")
    CALLBACKURL = environ.get("CALLBACKURL")
    DATABASEURL = environ.get("DATABASEURL")
    return API_KEY, TOKEN, CALLBACKURL, DATABASEURL

API_KEY, TOKEN, CALLBACKURL, DATABASEURL = loadConfig()


def get_db_user():
    users= models.User.query.all()
    for user in users:
        print(f"This is user with id = {user.id}")

    comments = models.Comment.query.all()
    for comment in comments:
        print(f'This is a comment with id = {comment.id}')

    webhooks = models.Webhook.query.all()
    for webhook in webhooks:
        print(f'This is a webhook with id = {webhook.id}')

    mirrors = models.Mirror.query.all()
    for mirror in mirrors:
        print(f'This is a mirror with id = {mirror.id}, original card = {mirror.original_card_id} and mirror = {mirror.mirror_card_id}')


    cards = models.Card.query.all()
    for card in cards:
        print(f'This is card with id = {card.id}')
    return print("done")


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



def getBoard(boardID):
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        BASEURL + "boards/{}".format(boardID),
        headers=headers,
        params=query
    )
    return response.json()


def getListName(listID):
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        BASEURL + "lists/{}".format(listID),
        headers=headers,
        params=query
    )
    return response.json()['name']


def getRootCard(cardID):
    print("prvi id: ", cardID)
    while True:
        result = (models.Mirror.query
                  .with_entities(models.Mirror.original_card_id)
                  .filter(models.Mirror.mirror_card_id == cardID)
                  .first())

        if not result:
            print("vracen id: ", cardID)
            return cardID  # If no parent exists, this is the root
        cardID = result[0]  # Move up the chain
        print("trenutni id: ", cardID)


def getDescendantCards(cardID, db):
    from sqlalchemy import text
    query = text("""
            WITH RECURSIVE descendants AS (
                SELECT mirror_card_id FROM mirror WHERE original_card_id = :cardID
                UNION ALL
                SELECT m.mirror_card_id FROM mirror m
                JOIN descendants d ON m.original_card_id = d.mirror_card_id
            )
            SELECT mirror_card_id FROM descendants;
        """)

    result = db.session.execute(query, {"cardID": cardID}).fetchall()

    # Convert result to a list of card IDs
    return [row[0] for row in result]

# TODO: Make sure to pass only the database session, not the whole db object
def getMirroredCards(cardID, db, onlyIDs = False):

    rootCardID = getRootCard(cardID)

    # just list of card ID's
    descendants = getDescendantCards(rootCardID, db)

    if cardID != rootCardID:
        descendants.append(rootCardID)
        descendants.remove(cardID)



    mirrors = []
    for c in descendants:
        mirrors.append(getCard(c))

    if onlyIDs:
        listOfIDs = []
        for mirror in mirrors:
            listOfIDs.append(mirror['id'])

        return listOfIDs
    # TODO: This is now uneccesarry because I get descendant card ID's
    # mirrors = models.Mirror.query.filter_by(original_card_id = rootCardID).all()

    res = {}
    # TODO: Change this build block
    for mirror in mirrors:
        _board = getBoard(mirror['idBoard'])
        _listName = getListName(mirror['idList'])

        _dic = {}
        _dic['name'] = mirror['name']
        _dic['shortURL'] = mirror['shortUrl']
        _dic['idBoard'] = mirror['idBoard']
        _dic['boardName'] = _board['name']
        _dic['boardURL'] = _board['shortUrl']
        _dic['listName'] = _listName

        res[mirror['id']] = _dic

    json_data = json.dumps(res, indent=4)

    print(json_data)

    return json_data

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

    # check if card exists in the database
    card = models.Card.query.get(idCardSource)

    if card == None:
        card = getCard(idCardSource)
        # TODO: Do I really need to have creator id in the database? I don't get that in the call to /getCard
        new_card = models.Card(id=idCardSource, name= card['name'], creator_id= 'boris.bastek')
        models.db.session.add(new_card)
        models.db.session.commit()



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


    # check if the card already has a webhook
    webhook_orig = models.Webhook.query.filter_by(card_id=idCardSource).first()
    if webhook_orig == None:
        webhook_orig = createWebhook(idCardSource)
        webhook_id = webhook_orig['id']
        # webhook_orig = {"id":"webhook_TEST"}
        new_webhook = models.Webhook(id=webhook_id, card_id=idCardSource)
        models.db.session.add(new_webhook)
        models.db.session.commit()


    # add card in cards table first
    mirroredCardId = response.json()["id"]
    card_name = response.json()['name']
    new_card = models.Card(id=mirroredCardId, name=card_name, creator_id="boris.bastek")
    models.db.session.add(new_card)
    models.db.session.commit()


    # create webhook for new card
    mirroredCardWebhook = createWebhook(mirroredCardId)
    mirror_webhook = models.Webhook(id=mirroredCardWebhook['id'], card_id=mirroredCardId)
    models.db.session.add(mirror_webhook)
    models.db.session.commit()


    # add cards to Mirror table
    new_mirror = models.Mirror(original_card_id=idCardSource , mirror_card_id=mirroredCardId)
    models.db.session.add(new_mirror)
    models.db.session.commit()

    return response.json()


def getComments(cardID, filter):
    url = "https://api.trello.com/1/cards/{}/actions".format(cardID)

    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    return response.json()


def syncronizeCards(req, cache):

    action = req["action"]
    model = req["model"]
    webhook = req["webhook"]


    responses = []

    changedCardId = model['id']

    affectedCards = getMirroredCards(changedCardId, models.db, onlyIDs=True)


    if action["type"] == 'updateCard':

        if action['display']['translationKey'] == 'action_renamed_card':

            identifier = action['id']
            cache.set(identifier, True, 180)

            # check the parent card
            for _cardID in affectedCards:
                response = updateCard(_cardID, name=model['name'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_changed_description_of_card':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, desc=model['desc'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_added_a_due_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, due=model['due'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_removed_a_due_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, due='null', identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_changed_a_due_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, due=model['due'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_added_a_start_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, start=model['start'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_removed_a_start_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, start='null', identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_changed_a_start_date':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, start=model['start'], identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_marked_the_due_date_complete':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, dueComplete=str(model['dueComplete']).lower(), identifier= identifier)
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_marked_the_due_date_incomplete':

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = updateCard(_card, dueComplete=str(model['dueComplete']).lower(), identifier= identifier)
                responses.append(response)

            return responses


    if action['type'] == 'addChecklistToCard':

        if action['display']['translationKey'] == 'action_add_checklist_to_card':

            # take the checklist source ID from the webhook
            idChecklistSource = action['data']['checklist']['id']

            identifier = action['id']
            cache.set(identifier, True, 180)

            for _card in affectedCards:
                response = createChecklist(cardID= _card, idChecklistSource= idChecklistSource, identifier= identifier)
                responses.append(response)

            return responses


    if action['type'] == 'removeChecklistFromCard':

        if action['display']['translationKey'] == 'action_remove_checklist_from_card':


            identifier = action['id']
            cache.set(identifier, True, 180)

            # TODO: Get the correct checklist to delete

            return






    if action['type'] == 'commentCard':
        if action['display']['translationKey'] == 'action_comment_on_card':

            identifier = action['id']
            cache.set(identifier, True, 300)

            initial_comment = models.Comment(id=action['id'], card_id=changedCardId, content=action['data']['text'], user_id=action['idMemberCreator'])
            models.db.session.add(initial_comment)
            models.db.session.commit()

            for _card in affectedCards:
                response = addCommentToCard(cardID=_card, comment=action['display']['entities']['comment']['text'], idenfitier= identifier)
                #TODO: Write the comment to the database
                new_comment = models.Comment(id=response['id'], card_id=response['data']['idCard'], content=response['data']['text'], user_id=response['idMemberCreator'])
                models.db.session.add(new_comment)
                models.db.session.commit()
                responses.append(response)

            return responses

    
    if action['type'] == 'updateComment':

        commentNewText = action['data']['action']['text']
        commentOldText = action['data']['old']['text']

        identifier = action['id']
        cache.set(identifier, True, 300)

        for _card in affectedCards:
            # for each card find a proper comment that needs updating
            _comments = getComments(cardID=_card, filter='commentCard')

            # find comment/action id
            _obsoleteCommentID = [x['id'] for x in _comments if x['data']['text'] == commentOldText][0]

            response = updateComment(cardID=_card, commentID=_obsoleteCommentID, text=commentNewText, identifier=identifier)
            #TODO: Write the update to the database
            models.Comment.query(id=_obsoleteCommentID).update({'content': f"{commentNewText}"})
            models.db.session.commit()
            responses.append(response)

        return responses


    if action['type'] == 'deleteComment':

        #TODO: Get comment from the database, find the same comment on other cards and then delete
        # on each card and then from the database
        commentoRemoveId = action['data']['action']['id']
        cardCommentIsOn = action['data']['card']['id']

        identifier = action['id']
        cache.set(identifier, True, 300)

        for _card in affectedCards:
            # for each card find a proper comment that needs updating
            _comments = getComments(cardID=_card, filter='commentCard')

            # find comment/action id
            _obsoleteCommentID = ''







def updateCard(id, name=None, desc=None, closed=None, idMembers=None, idAttachmentCover=None, idList=None, idLabels=None,
               idBoard=None, pos=None, due=None, start=None, dueComplete=None, subscribed=None, address=None,
               locationName=None, coordinates=None, cover=None, identifier=None):
    """
    Updates the card with the given ID.
    """
    params = locals()
    headers = {
        "Accept": "application/json"
    }

    if identifier:
        headers['X-Trello-Client-Identifier'] = identifier

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



def addCommentToCard(cardID, comment, idenfitier):
    url = "https://api.trello.com/1/cards/{}/actions/comments".format(cardID)

    headers = {
        "Accept": "application/json",
        "X-Trello-Client-Identifier": idenfitier
    }

    query = {
        'text': comment,
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )

    print("Added comment")
    return response.json()



def updateComment(cardID, commentID, text, identifier):
    url = "https://api.trello.com/1/cards/{}/actions/{}/comments".format(cardID, commentID)

    headers = {
        "Accept": "application/json",
        "X-Trello-Client-Identifier": identifier
    }

    query = {
        'text': text,
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "PUT",
        url,
        headers=headers,
        params=query
    )

    print(response.text)
    return response.json()


def deleteComment(cardID, commentID):
    url = "https://api.trello.com/1/cards/{}/actions/{}/comments".format(cardID, commentID)

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "DELETE",
        url,
        params=query
    )

    print(response.text)
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
    print('Webhook created with id = ', response.json()['id'])
    return response.json()


def createChecklist(cardID, name=None, pos=None, idChecklistSource=None, identifier=None):

    params = locals()
    headers = {
        "Accept": "application/json",
        "X-Trello-Client-Identifier": identifier
    }

    query = {
        'idCard': cardID,
        'key': API_KEY,
        'token': TOKEN
    }

    # works for now, it just takes all parameters and adds them to the query
    query.update(params)

    response = requests.request(
        "POST",
        BASEURL + "checklists",
        headers=headers,
        params=query
    )

    print(response.json())
    return response.json()


def deleteChecklist(checklistID):

    headers = {
        "Accept": "application/json",
    }

    query = {
        'key': API_KEY,
        'token': TOKEN
    }

    response = requests.request(
        "DELETE",
        BASEURL + "checklists/{}".format(checklistID),
        headers=headers,
        params=query
    )

    print(response.json())
    return response.json()