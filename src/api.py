import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, init_mgmt

app = Flask(__name__)
setup_db(app)
CORS(app)
auth0 = init_mgmt()

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, PATCH, POST, DELETE, OPTIONS')

    return response

# db_drop_and_create_all()

# Return users matching a role


def users_by_role(role):
    roles = []
    for user in auth0.users.list()['users']:
        user_roles = auth0.users.list_roles(user['user_id'])
        for user_role in user_roles['roles']:
            if user_role['name'].lower() in role:
                roles.append(user)
    return roles


def get_user_by_id(id, users):
    for user in users:
        if user['user_id'] == id:
            return user

    return None

# ROUTES
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
        drink = Drink(
            title=body.get('title'),
            recipe=json.dumps(
                body.get('recipe')))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except BaseException:
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
    except BaseException:
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
    except BaseException:
        abort(422)


# Management routes
@app.route('/users')
@requires_auth('manage:barista, manage:manager')
def get_users(role):
    users_list = users_by_role(role)

    return jsonify({
        'success': True,
        'total_users': len(users_list),
        'users': users_list
    })


@app.route('/users/<id>')
@requires_auth('manage:barista, manage:manager')
def get_user(role, id):
    users = users_by_role(role)
    user = get_user_by_id(id, users)

    if not user:
        raise AuthError({
            'code': '404',
            'description': 'User not found \
                or missing permission to access resource.'
        }, 404)

    return jsonify({
        'success': True,
        'users': user
    })


@app.route('/users/<id>', methods=['DELETE'])
@requires_auth('manage:barista, manage:manager')
def delete_user(role, id):
    users = users_by_role(role)
    user = get_user_by_id(id, users)
    if not user:
        raise AuthError({
            'code': '404',
            'description': 'User not found \
                or missing permission to access resource.'
        }, 404)

    auth0.users.delete(id)

    return jsonify({
        'deleted': id
    })


@app.route('/users', methods=['POST'])
@requires_auth('manage:barista, manage:manager')
def create_user(role):
    body = request.get_json()
    user = {
        'email': body.get('email'),
        'email_verified': False,
        'name': body.get('name'),
        'nickname': body.get('nickname'),
        'picture': body.get('picture'),
        'connection': 'Username - Password - Authentication',
        'password': body.get('password'),
        'blocked': False,
        'verify_email': False
    }
    created_user = auth0.users.create(user)

    return jsonify({
        'success': True,
        'created': created_user
    })


@app.route('/users/<id>', methods=['PATCH'])
@requires_auth('manage:barista, manage:manager')
def edit_user(role, id):
    body = request.get_json()
    to_be_updated = {}

    users = users_by_role(role)
    user = get_user_by_id(id, users)

    if not user:
        raise AuthError({
            'code': '404',
            'description': 'User not found \
            or missing permission to access resource.'
        }, 404)

    if body.get('blocked'):
        to_be_updated['blocked'] = body.get('blocked')
    if body.get('email'):
        to_be_updated['email'] = body.get('email')
    if body.get('name'):
        to_be_updated['name'] = body.get('name')
    if body.get('nickname'):
        to_be_updated['nickname'] = body.get('nickname')
    if body.get('picture'):
        to_be_updated['picture'] = body.get('picture')
    if body.get('password'):
        to_be_updated['password'] = body.get('password')

    updated_user = auth0.users.update(id, to_be_updated)

    return jsonify({
        'success': True,
        'users': updated_user
    })

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(405)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405


@app.errorhandler(401)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
    }), 500


@app.errorhandler(AuthError)
def auth_error(auth_res):
    return jsonify({
        'success': False,
        'error': auth_res.error['code'],
        'message': auth_res.error['description']
    }), auth_res.status_code
