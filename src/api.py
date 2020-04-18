import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS Headers 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
        'GET, PATCH, POST, DELETE, OPTIONS')

    return response

db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    body = request.get_json()
    try:
        drink = Drink(title=body.get('title'), recipe=json.dumps(body.get('recipe')))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        if title:
            drink.title = body['title']
        if recipe:
            drink.recipe = json.dumps(body['recipe'])
            
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        })
    except:
        abort(422)

## Error Handling
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
                    "message": "resource not found"
                    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "internal server error"
                    }), 500

@app.errorhandler(AuthError)
def auth_error(auth_res):
    return jsonify({
                    "success": False, 
                    "error": auth_res.error['code'],
                    "message": auth_res.error['description']
                    }), auth_res.status_code