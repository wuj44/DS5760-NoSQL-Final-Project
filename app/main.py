'''Final Project'''

# Module for serving API requests
from app import app
from bson.json_util import dumps, loads
from flask import request, jsonify
import json
import ast # helper library for parsing data from string
from importlib.machinery import SourceFileLoader
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import pandas as pd

client = MongoClient(host="localhost", port=27017)

# Import the utils module
utils = SourceFileLoader('*', './app/utils.py').load_module()

# Select the database
db = client.mydb
# Select the collection
collection_iphone = db.iphone
collection_keyboard = db.keyboard


# route decorator that defines which routes should be navigated to this function
@app.route("/") # '/' for directing all default traffic to this function get_initial_response()
def get_initial_response():

    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the final project on MongoDB with Web API'
    }
    resp = jsonify(message)
    # Returning the object
    return resp


@app.route("/api/v1/fp/<item>/<start_date>/<end_date>", methods=['GET'])
def fetch_item_span(item, start_date, end_date):
    '''
       Function to fetch records within a specific date_first_available span
    '''
    collection = collection_iphone if item=='iphone' else collection_keyboard
    try:
        # Call the function from utils to get the query params
        # query_params = utils.parse_query_params(request.query_string)
        query_params = {"date_first_available": {"$gte": str(start_date), "$lte": str(end_date)}}

        # Check if records were found in DB
        if collection.count_documents(query_params) > 0:
            # fetch customers by query parameters
            records_fetched = collection.find(query_params)

            # Prepare the response
            return dumps(records_fetched)
        else:
            return 'No records are found', 404

    except Exception as e:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return e, 500


@app.route("/api/v1/fp/<item>/<param>/<num>/<ascending>", methods=['GET'])
def fetch_item_sort(item, param, num, ascending):
    '''
       Function to fetch top n records in an ascending order based on price
    '''
    collection = collection_iphone if item=='iphone' else collection_keyboard
    try:
        # find number of records of which price>0
        prices = collection.count_documents({str(param): {"$gt": 0}})
        # Check if records were found in DB
        if prices > 0:
            num = int(num) if int(num) <= prices else prices
            # fetch records by query parameters
            records_fetched = collection.find().sort(str(param), int(ascending)).limit(num)
            # Prepare the response
            return dumps(records_fetched)
        else:
            return 'No records are found', 404

    except Exception as e:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return e, 500


@app.route("/api/v1/fp/<cat>/<item>/<price>/create", methods=['POST'])
def create_item(cat, item, price):
    '''
       Function to create a new item
    '''
    collection = collection_iphone if cat == 'iphone' else collection_keyboard
    
    try:
        # Create a new item
        try:
            # Set params
            body = {"item":str(item), "price":float(price), "last_modified":datetime.datetime.utcnow()}
        except Exception as e:
            # Bad request as request body is not available
            # Add message for debugging purpose
            print(e)
            return "", 400
        # Insert the record
        record_created = collection.insert_one(body)
        inserted_id = record_created.inserted_id
        # Return id of the newly created item
        return jsonify(str(inserted_id)), 201
    except Exception as e:
        # Error while trying to create customers
        # Add message for debugging purpose
        print(e)
        return 'Server error', 500


@app.route("/api/v1/fp/<cat>/<objid>/<item>/<price>/replace", methods=['POST'])
def replace_item(cat, objid, item, price):
    '''
       Function to replace an incorrectly created item
    '''
    collection = collection_iphone if cat == 'iphone' else collection_keyboard
    
    try:
        try:
            # Set new params
            body = {"item":str(item), "price":float(price), "last_modified":datetime.datetime.utcnow()}
            query_params = {'_id':ObjectId(objid)}
        except Exception as e:
            # Bad request as request body is not available
            # Add message for debugging purpose
            print(e)
            return "", 400
        # Replace the record based on the id
        records_updated = collection.replace_one(query_params, body)
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return records_updated.raw_result, 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return 'No modification was made', 304
    except Exception as e:
        # Error while trying to update the resource
        # Add message for debugging purpose
        print(e)
        return 'Server error', 500


@app.route("/api/v1/fp/<item>/<input_date>/<discount>/update_price", methods=['POST'])
def update_price(item, input_date, discount):
    '''
       Function to update the price
    '''
    collection = collection_iphone if item == 'iphone' else collection_keyboard
    try:
        # Get the value which needs to be updated
        try:
            # Set params for updating
            body = {"$mul": {"price": 1-int(discount)/100}, "$set": {'last_modified': datetime.datetime.utcnow()}}
            print(body)
        except Exception as e:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return '', 400
        # Set params for finding
        query_params = {"date_first_available": {"$lt": input_date}}
        # Update the records
        records_updated = collection.update_many(query_params, body)
        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return records_updated.raw_result, 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return 'No modification was made', 304
    except Exception as e:
        # Error while trying to update the resource
        # Add message for debugging purpose
        print(e)
        return 'Server error', 500


@app.route("/api/v1/fp/<item>/<param>/<val>/update_overview", methods=['POST'])
def update_overview(item, param, val):
    '''
       Function to update the overview
    '''
    collection = collection_iphone if item == 'iphone' else collection_keyboard
    try:
        # Get the value which needs to be updated
        try:
            body = {"$set": {"overview": val, 'last_modified': datetime.datetime.utcnow()}}
            print(body)
        except Exception as e:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return '', 400

        # Updating the record based on the id
        records_updated = collection.update_one({"_id": ObjectId(param)}, body)

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return records_updated.raw_result, 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return 'No modification was made', 304
    except Exception as e:
        # Error while trying to update the resource
        # Add message for debugging purpose
        print(e)
        return 'Server error', 500


@app.route("/api/v1/fp/<item>/<input_id>/remove", methods=['DELETE'])
def remove_user(item, input_id):
    """
       Function to remove the record based on the id
       """
    collection = collection_iphone if item=='iphone' else collection_keyboard
    try:
        # Delete the record
        delete_user = collection.delete_one({"_id": ObjectId(input_id)})
        print(delete_user.raw_result)
        if delete_user.deleted_count > 0 :
            # Prepare the response
            return 'Record removed', 204
        else:
            # Resource not found
            return 'Record not found', 404
    except Exception as e:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        print(e)
        return "", 500


@app.errorhandler(404)
def page_not_found(e):
    '''Send message to the user if route is not defined.'''

    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }

    resp = jsonify(message)
    # Sending 404 (not found) response
    resp.status_code = 404
    # Returning the object
    return resp