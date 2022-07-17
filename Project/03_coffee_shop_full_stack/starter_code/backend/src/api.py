import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

#GET /drinks:
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [d.short() for d in drinks]
        }),200
    except:
        return jsonify({
            'success': False,
            'error': "An Error Occurred"
        }), 500
   


#GET /drinks-details
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [d.long() for d in drinks]
        }), 200

    except:
        return jsonify({
            'success': False,
            'error': "An Error Occurred"
        }), 500



#POST /drinks
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    
    request = request.get_json()
    try:
        drink = Drink()
        drink.title = request['title']
        drink.recipe = json.dumps(request['recipe'])
        drink.insert()

        return jsonify({
            'success': True,
             'drinks': [drink.long()]
        }), 200

    except:
        abort(400)

    



#PATCH /drinks/<id>
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id, payload):
    request = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.title = request['title']
        drink.recipe = request['recipe']
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)


#DELETE /drinks/<id>
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def drinks(id, payload):
    drink = Drink.query.filter(Drink.id == id)
    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        })

    except:
        abort(422)


#---------------------------------------#
#Error handlers
#---------------------------------------#
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401



@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable"
        }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
