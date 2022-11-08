import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import setup_db, Drink, db
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
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    dict_drinks = [drink.short() for drink in drinks]
    print(drinks)
    return jsonify({
        "Success": True, 
        "drinks": dict_drinks
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()
    dict_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "Success": True, 
        "drinks": dict_drinks
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
def create_drinks():

    data = request.get_json()
    name = data['name']
    color = data['color']
    parts = data['parts']

    #drinks = '[{"name": name, "color": color, "parts": parts}]'

    drink_recipe = '"name": "{}", "color": "{}", "parts": {}'.format(name, color, parts)
    
    drink = '[{'+drink_recipe+'}]'

    new_drink = Drink(title=name.capitalize(), recipe=str(drink))

    new_drink.insert()
    db.session.close()

    # drinks = ["name": "black coffee", "color": "dark brown", "parts": 1]
    return jsonify({
        "Success": True, 
        "drinks": str(drink)
        })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
def edit_drinks(id):

    data = request.get_json()

    drink = Drink.query.filter_by(id=id).first()
    recipe_dict = drink.long()['recipe'][0]

    if "name" in data.keys():
        recipe_dict['name'] = data['name']

    if "color" in data.keys():
        recipe_dict['color'] = data['color']
    
    if "parts" in data.keys():
        recipe_dict['parts'] = data['parts']


    recipe = '"name": "{name}", "color": "{color}", "parts": {parts}'.format(**recipe_dict)
    
    drink.recipe = '[{'+recipe+'}]'

    drink.update()
    db.session.close()

    drink = Drink.query.filter_by(id=id).first()

    return jsonify({
        "Success": True, 
        "drinks": drink.long()
        })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drinks(id):
    drink = Drink.query.filter_by(id=id).first()
    drink.delete()
    return jsonify({
        "Success": True, 
        "delete": drink.id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found():
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found" 
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
