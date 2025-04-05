from asyncio import timeout

from flask import request, render_template, jsonify
import core
from flask_caching import Cache



def register_routes(app, db, cache):

    @app.route('/', methods=['GET', 'POST'])  # Accepts only POST requests
    def example():
        return render_template('index.html')

    @app.route('/test', methods=['GET', 'POST'])  # Accepts only POST requests
    def test():
        return render_template('test.html')

    @app.route('/getBoards', methods=['GET'])  # Accepts only POST requests
    def getBoards():
        return core.getBoards()


    @app.route('/getFilteredListsOnBoard', methods=['GET'])  # Accepts only POST requests
    def getFilteredListOnBoard():
        boardID = request.args.get('boardID')
        filter = 'open'
        return core.getFilteredListsOnBoard(boardID, filter)


    @app.route('/createMirrorCard', methods=['POST'])
    def createMirrorCard():
        req = request.get_json()
        idList = req["listID"]
        idCardSource = req["originalCardID"]
        return core.createMirrorCard(listID=idList, idCardSource=idCardSource)

    @app.route('/getMirroredCards', methods=['GET'])
    def getMirroredCards():
        cardID = request.args.get('cardID')
        return core.getMirroredCards(cardID, db)


    @app.route('/webhook', methods=['POST'])
    def receiveChange():

        try:
            req = request.get_json()
        except Exception as error:
            return f"Could not read the response: {error}", 400

        client_identifier = request.headers.get("X-Trello-Client-Identifier")

        if cache.get(client_identifier):
            print("Action already in cache, ignoring the webhook")
            return f"Action already in cache {client_identifier}, ignoring the webhook", 200

        # if cache.get(req['action']['id']):
        #     print("Action already procesed, ignoring the webhook")
        #     return f"Action already already procesed {client_identifier}, ignoring the webhook", 200

        result = core.syncronizeCards(req, cache)
        return jsonify(result)