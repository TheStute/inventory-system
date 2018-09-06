from pymongo import MongoClient
from flask import Flask, request, render_template, redirect, url_for
import json
from bson.objectid import ObjectId

mongoUser = ''
mongoPass = ''
with open('secrets.json','r') as f:
    config = json.load(f)
    mongoUser = config['mongo']['username']
    mongoPass = config['mongo']['password']
client = MongoClient(f'mongodb+srv://{mongoUser}:{mongoPass}@stuteinventory-vckb7.mongodb.net/test?retryWrites=true')
db = client.inventory
items = db.items

app = Flask(__name__)

"""
Routes:
/ GET POST
+{id} GET PATCH DELETE
"""
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        things = [thing for thing in items.find({})]
        return render_template('index.html',things=things, state=request.args.get('state'), itemId=request.args.get('id'))
    elif request.method == "POST":
        newItemDict = {
            'name': request.form['name'],
            'location': request.form['location'],
            'notes': request.form['notes']
        }
        newItem = items.insert_one(newItemDict)
        return redirect(f'/?state=new&id={newItemDict["name"]}')
    return "invalid"

@app.route("/<itemId>", methods=["GET","POST"])
def singleItem(itemId):
    if request.method == "GET":
        thing = items.find_one({'_id': ObjectId(itemId)})
        return render_template('item.html',thing=thing, state=request.args.get('state'), op=request.args.get('op'))
    elif request.method == "POST":
        if request.form.get('_method') == "PATCH":
            updatedItemDict = { '$set': {
                'name': request.form['name'],
                'location': request.form['location'],
                'notes': request.form['notes']
            }}
            updatedItem = items.update_one({'_id': ObjectId(itemId)}, updatedItemDict)
            if updatedItem.modified_count == 1:
                return redirect(f'/{itemId}?state=updated')
            else:
                return redirect(f'/{itemId}?state=failed&op=update')
        elif request.form.get('_method') == "DELETE":
            deletedItem = items.find_one_and_delete({'_id': ObjectId(itemId)})
            if deletedItem:
                return redirect(f'/?state=deleted&id={deletedItem.get("name")}')
            else:
                return redirect(f'/{itemId}?state=failed&op=delete')
    return "invalid"

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080)
