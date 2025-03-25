import requests
import json

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
def getMirroredCards(cardID, db):

    rootCardID = getRootCard(cardID)

    # just list of card ID's
    descendants = getDescendantCards(rootCardID, db)

    if cardID != rootCardID:
        descendants.append(rootCardID)
        descendants.remove(cardID)



    mirrors = []
    for c in descendants:
        mirrors.append(getCard(c))


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

def syncronizeCards(req):
    action = req["action"]
    model = req["model"]
    webhook = req["webhook"]

    # check the changes / caching / ignoring duplicate updates

    responses = []

    changedCardId = model['id']

    # get mirrored cards for the changed card
    copied = models.Mirror.query.filter_by(original_card_id=changedCardId).all()
    # gets the ID of the "child" card of the current card
    # models.Mirror.query.filter_by(original_card_id=changedCardId).all()[0].mirror_card_id


    isCopyOf = models.Mirror.query.filter_by(mirror_card_id=changedCardId).all()
    # gets the ID of "parent" card of the changed card
    # models.Mirror.query.filter_by(mirror_card_id=changedCardId).all()[0].original_card_id

    # mirroredCardsList = database['cards'][changedCardId]['mirroredCards']

    if action["type"] == 'updateCard':

        if action['display']['translationKey'] == 'action_renamed_card':
            # first check the child card
            for _card in copied:
                response = updateCard(_card.mirror_card_id, name=model['name'])
                responses.append(response)

            # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, name=model['name'])
                responses.append(response)

            return responses

        if action['display']['translationKey'] == 'action_changed_description_of_card':
            for _card in copied:
                response = updateCard(_card.mirror_card_id, desc=model['desc'])
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, desc=model['desc'])
                responses.append(response)

            return responses

        if action['display']['translationKey'] == 'action_added_a_due_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, due=model['due'])
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, due=model['due'])
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_removed_a_due_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, due='null')
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, due='null')
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_changed_a_due_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, due=model['due'])
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, due=model['due'])
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_added_a_start_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, start=model['start'])
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, start=model['start'])
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_removed_a_start_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, start='null')
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, start='null')
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_changed_a_start_date':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, start=model['start'])
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, start=model['start'])
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_marked_the_due_date_complete':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)

            return responses


        if action['display']['translationKey'] == 'action_marked_the_due_date_incomplete':

            for _card in copied:
                response = updateCard(_card.mirror_card_id, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)

                # check the parent card
            for _card in isCopyOf:
                response = updateCard(_card.original_card_id, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)

            return responses


    if action['type'] == 'addChecklistToCard':

        if action['display']['translationKey'] == 'action_add_checklist_to_card':


            # first check the child card
            for _card in copied:
                response = createChecklist(cardID= _card.mirror_card_id, idChecklistSource= changedCardId)
                responses.append(response)

            # check the parent card
            for _card in isCopyOf:
                response = createChecklist(cardID= _card.original_card_id, idChecklistSource= changedCardId)
                responses.append(response)

            return responses


    # TODO: Comments will be updated later
    if action['type'] == 'commentCard':
        if action['display']['translationKey'] == 'action_comment_on_card':

            _database['cards'][changedCardId]['comments'].append(action['id'])
            with open('database.json', 'w') as file:
                json.dump(_database, file, indent=4)

            # get the card that comment was made in
            numberOfComments = int(model['badges']['comments'])
            # get the numbers for mirrored cards
            cardsToUpdate = []
            for cardId in mirroredCardsList:
                _card = getCard(cardId)
                if int(_card['badges']['comments']) != numberOfComments:
                    cardsToUpdate.append(cardId)

            if len(cardsToUpdate) == 0:
                print('COMMENTS UP TO DATE')
                return {'Error': "Comments already up to date. Same number of comments on all cards"}

            for cardId in cardsToUpdate:
                response = addCommentToCard(cardID=cardId, comment=action['display']['entities']['comment']['text'])
                _database['cards'][cardId]['comments'].append(response['id'])
                with open('database.json', 'w') as file:
                    json.dump(_database, file, indent=4)
                responses.append(response)
            return responses
    
    if action['type'] == 'updateComment':
        commentID = action['data']['action']['id']
        commentText = action['data']['action']['text']





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



def addCommentToCard(cardID, comment):
    url = "https://api.trello.com/1/cards/{}/actions/comments".format(cardID)

    headers = {
        "Accept": "application/json"
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


def createChecklist(cardID, name=None, pos=None, idChecklistSource=None):

    params = locals()

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
        params=query
    )

    print(response.json)
    return response.json