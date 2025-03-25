from flask import request, render_template
import core



def register_routes(app, db):

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
        # TODO: Check if the req is serializable
        try:
            req = request.get_json()
            return core.syncronizeCards(req)
        except:
            print("problem is here")
            return {"ERROR, not serializable!"}
