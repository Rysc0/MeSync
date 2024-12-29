# app.py

from flask import Flask, request
import core

# this will do as a temporary database of cards
# each card ID has list of other cardID's that are mirrors
DATABASE = {"":""}

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if request.json["action"]["type"] == "updateCard":
            core.updateCardAction(request.json)
        print("Data received from Webhook is: ", request.json)
        return "Webhook received!"

app.run(host='0.0.0.0', port=8123)