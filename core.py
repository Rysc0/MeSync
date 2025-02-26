import requests
import json

# database imports
import models
#
# with open("database.json") as db:
#     database = json.load(db)

def loadConfig():
    with open("config.json", "r") as cfg:
        data = json.load(cfg)
        API_KEY = data["API_KEY"]
        TOKEN = data["TOKEN"]
        CALLBACKURL = data["CALLBACKURL"]
        DATABASEURL = data["DATABASEURL"]
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
    new_card = models.Card(id=mirroredCardId, name="Boris", creator_id="boris.bastek")
    models.db.session.add(new_card)
    models.db.session.commit()


    # create webhook for new card
    mirroredCardWebhook = createWebhook(mirroredCardId)
    mirror_webhook = models.Webhook(id=mirroredCardWebhook['id'], card_id=mirroredCardId)
    models.db.session.add(mirror_webhook)
    models.db.session.commit()
    # mirroredCardWebhook = {'id': '11111111'}
    print("mirrored webhook: ", mirroredCardWebhook['id'])


    # add cards to Mirror table
    new_mirror = models.Mirror(original_card_id=idCardSource , mirror_card_id=mirroredCardId)
    models.db.session.add(new_mirror)
    models.db.session.commit()

    return response.json()

def syncronizeCards(req):
    action = req["action"]
    model = req["model"]
    webhook = req["webhook"]

    with open('database.json', 'r') as _db:
        _database = json.load(_db)

    responses = []

    changedCardId = model['id']

    mirroredCardsList = database['cards'][changedCardId]['mirroredCards']

    if action["type"] == 'updateCard':

        if action['display']['translationKey'] == 'action_renamed_card':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, name=model['name'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_changed_description_of_card':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, desc=model['desc'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_added_a_due_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, due=model['due'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_removed_a_due_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, due='null')
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_changed_a_due_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, due=model['due'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_added_a_start_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, start=model['start'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_removed_a_start_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, start='null')
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_changed_a_start_date':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, start=model['start'])
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_marked_the_due_date_complete':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)
            return responses

        if action['display']['translationKey'] == 'action_marked_the_due_date_incomplete':
            for cardId in mirroredCardsList:
                response = updateCard(cardId, dueComplete=str(model['dueComplete']).lower())
                responses.append(response)
            return responses

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