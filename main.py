import json
from bson.objectid import ObjectId

from pdfgen import PDFGen
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as pymongoDupKey
from flask import Flask, request, render_template, redirect, url_for

mongoUser = ''
mongoPass = ''
with open('secrets.json','r') as f:
    config = json.load(f)
    mongoUser = config['mongo']['username']
    mongoPass = config['mongo']['password']
client = MongoClient(f'mongodb+srv://{mongoUser}:{mongoPass}@stuteinventory-vckb7.mongodb.net/test?retryWrites=true')
items = client.inventory.items
items.create_index('name', unique=True)

LOCATIONS = {
    '0': 'Jacobus',
    '1': 'In Transit',
    '2': 'Alexander',
    '3': 'Other'
}

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        things = [thing for thing in items.find({})]
        return render_template('index.html',things=things, state=request.args.get('state'), itemId=request.args.get('id'), locations=LOCATIONS)
    elif request.method == "POST":
        newItemDict = {
            'name': request.form['name'],
            'location': request.form['location'],
            'notes': request.form['notes']
        }
        try:
            newItem = items.insert_one(newItemDict)
        except pymongoDupKey:
            return redirect(f'/?state=failed&id=Item%20with%20name%20already%20exists')
        return redirect(f'/?state=new&id={newItemDict["name"]}')
    return "invalid"

@app.route("/<itemId>", methods=["GET","POST"])
def singleItem(itemId):
    if itemId=='favicon.ico':
        return app.send_static_file('favicon.ico')
    if request.method == "GET":
        thing = items.find_one({'_id': ObjectId(itemId)})
        return render_template('item.html',thing=thing, state=request.args.get('state'), op=request.args.get('op'), locations=LOCATIONS)
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

@app.route("/generate", methods=["GET","POST"])
def pdfGen():
    things = [thing for thing in items.find({})]
    if request.method == "GET":
        return render_template('generator.html',things=things)
    elif request.method == "POST":
        itemIds = request.form.getlist('items')
        return redirect(PDFGen([thing for thing in things if str(thing.get('_id')) in itemIds]))
    return "invalid"

@app.route("/scan")
def scanner():
    return render_template('scan.html')

if __name__ == "__main__":
    app.run('0.0.0.0', port=80)
