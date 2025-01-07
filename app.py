# app.py
import flask
from flask import Flask, request, render_template
import core
from flask_cors import CORS


# this will do as a temporary database of cards
# each card ID has list of other cardID's that are mirrors
DATABASE = {"":""}

app = Flask(__name__)
CORS(app) #, origins="https://trello.com")

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if request.json["action"]["type"] == "updateCard":
            core.updateCardAction(request.json)
        print("Data received from Webhook is: ", request.json)
        return "Webhook received!"
    
    
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
    return core.createMirrorCard(listID=idList, originalCardID=idCardSource)

app.run(host='0.0.0.0', port=8123, debug=True)