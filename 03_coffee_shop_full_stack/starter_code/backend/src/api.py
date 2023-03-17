import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.http import HTTP_STATUS_CODES
# from exceptions import AuthError

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES

@app.route("/drinks", methods=["GET"])
@requires_auth('get:drinks')
def retrieve_drinks(payload):
    try:

        drinks = Drink.query.order_by(Drink.id).all()     

        if len(drinks) == 0:
            abort(404)
 
        return jsonify(
            {
                "success": True,
                "drinks": [drink.short() for drink in drinks]
            }
        )
    except Exception as error:
        print(error)
        abort(422)

@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()     
      
        if len(drinks) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }
        )
    except Exception as error:
        print(error)
        abort(422)

@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def insert_drinks(payload):
    try:
    
        body = request.get_json()
        new_title = body.get("title", None)
        recipe = body.get("recipe")
        new_recipe = json.dumps(recipe)
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
    
        return jsonify({
            "success": True,
             "drinks": [drink.long()]
        })
    
    except Exception as error:
        print(error)
        abort(422)


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drinks(payload,id):
    try:

        body = request.get_json()
        new_title = body.get("title", None)
        recipe = body.get("recipe")
        
        
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink:
            if new_title:
                drink.title = new_title
            if recipe:
                new_recipe = json.dumps(recipe)
                drink.recipe = new_recipe
            drink.update()
        
            return jsonify({
                "success": True,
                "drinks": [drink.long()]
            })
        else:
            abort(404)
    
    except Exception as error:
        print(error)
        abort(422)


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(payload,id):
    try:

        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink:
            drink.delete()
            return jsonify({
                "success": True,
                "delete": id
            })
        else:
            abort(404)
    
    except Exception as error:
        print(error)
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404, 
        "message": "resource not found"}), 404



@app.errorhandler(AuthError)
def handle_auth_error(err):
    response = {
        "message": HTTP_STATUS_CODES.get(err.status_code),
        "description": err.error,
    }
    return response, err.status_code