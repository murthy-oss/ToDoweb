from flask import Flask, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

from config import *

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
database = client[MONGODB_DATABASE_NAME]
items_collection = database[MONGODB_TODO_ITEMS_COLLECTION]

@app.get("/get_todo_items")
def get_todo_items():
    try:
        items_list = items_collection.find()
        items_list = [{"id": str(item["_id"]), "content": item["content"]} for item in items_list]
        return jsonify({
        "todoItems": items_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/")
def home():
    return "Welcome to the app!"


@app.post("/add_todo_item")
def add_todo_item():
    item_content = request.json["item_content"]
    _id = items_collection.insert_one({"content": item_content})

    return jsonify({
        "item_id": str(_id.inserted_id)
    })

@app.post("/delete_todo_item")
def delete_todo_item():
    item_id = request.json["item_id"]
    items_collection.delete_one({"_id": ObjectId(item_id)})
    return {}

@app.post("/update_todo_item")
def update_todo_item():
    item_id = request.json["item_id"]
    new_content = request.json["item_content"]
    
    # Update the todo item in the database
    result = items_collection.update_one(
        {"_id": ObjectId(item_id)}, 
        {"$set": {"content": new_content}}
    )

    # Check if the update was successful
    if result.modified_count > 0:
        return jsonify({"message": "Todo item updated successfully"})
    else:
        return jsonify({"message": "Todo item not found or no change made"}), 404

