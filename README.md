# Coffee Shop Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment . This keeps your dependencies for each project separate and organaized.

```bash
pip install virtualenv
cd YOUR_PROJECT_DIRECTORY_PATH/
virtualenv env
source env/bin/activate
```
More instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## API REFERENCE

### Endpoints

- GET '/drinks'
- GET '/drinks-detail'
- POST '/drinks'
- PATCH '/drinks/{drink_id}'
- DELETE '/drinks/{drink_id}'
- GET '/users'
- POST '/users'
- GET '/users/{user_id}'
- DELETE '/users/{user_id}'
- PATCH '/users/{user_id}'


##### GET '/drinks'
- Fetches an array of available drinks with short format.
- Request Arguments: None
- Requires permissions: None
- Returns: An array with success and list of drinks. 

```json
{
  "drinks": [
    {
      "id": 2,
      "recipe": [
        {
          "color": "black",
          "parts": 1
        }
        ...
      ],
      "title": "Coffee"
    }
    ...
  ],
  "success": true
}

```
##### GET '/drinks-detail'

- Fetches an array of available drinks with long format.
- Request Arguments: None
- Requires permissions: `get:drinks-detail`
- Returns: An array with success and list of drinks in long format.

##### POST '/drinks'
- Creates a new drink.
- Request Arguments: 
    - title: String
    - recipe: Array
        - color: String
        - parts: Integer
        - name: String
- Requires permissions: `post:drinks`
- Returns: An object with success, and the newly created drink.

```json
{
  "success": true,
  "drinks": [
    {
      "id": 2,
      "recipe": [
        {
          "color": "black",
          "parts": 1
        }
      ],
      "title": "Coffee"
    }
  ]
}
```

##### DELETE '/drinks/{drink_id}'

- Deletes a drink with the id provided in the URI.
- Request Arguments: None
- Requires permissions: `delete:drinks`
- Returns: And object with success and deleted which contains the deleted drink id 

```json
{
  "success": true,
  "deleted": 2
}
```


##### PATCH '/drinks/{drink_id}'

- Modifies an existing drink.
- Request Arguments:
    - title: String
    - recipe: Array
        - color: String
        - parts: Integer
        - name: String
- Requires permissions: `patch:drinks`
- Returns: An array with success and list of drinks in long format.

```json
{
  "success": true,
  "drinks": [
    {
      "id": 2,
      "recipe": [
        {
          "color": "black",
          "parts": 1
        }
      ],
      "title": "Coffee"
    }
  ]
}
```

##### GET '/users'

- Get a list of existing users in the auth0 database.
- Request Arguments: None
- Requires permissions: `manage:barista` and/or `manage:manager`
- Returns: An object with a success key, total_users and list of users.

```json
{
  "success": true,
  "total_users": 3,
  "users": [
    {
      "created_at": "2020-04-17T23:24:43.499Z",
      "email": "manager@udacoffeeshop.com",
      "email_verified": false,
      "identities": [
        {
          "connection": "Username-Password-Authentication",
          "isSocial": false,
          "provider": "auth0",
          "user_id": "5e9a3abb152a670c21497258"
        }
      ],
      "last_ip": "41.249.52.37",
      "last_login": "2020-04-20T16:12:22.415Z",
      "logins_count": 4,
      "multifactor": [
        "guardian"
      ],
      "multifactor_last_modified": "2020-04-17T23:25:50.934Z",
      "name": "manager@udacoffeeshop.com",
      "nickname": "manager",
      "picture": "https://s.gravatar.com/avatar/5bd3fbf085699285359fbe69e4f3d705?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
      "updated_at": "2020-04-20T16:12:22.415Z",
      "user_id": "auth0|5e9a3abb152a670c21497258"
    },
    ...
  ]
}
```
##### POST '/users'
- Creates a new user and save it to the auth0 database.
- Request Arguments: 
    - email: String
    - name: String
    - nickname: String
    - picture: String
    - password: String
- Requires permissions: `manage:barista` and/or `manage:manager`
- Returns: An object with success, and the newly created user.

```json
{
  "success": true,
  "created": {
      "created_at": "2020-04-17T23:24:43.499Z",
      "email": "manager@udacoffeeshop.com",
      "email_verified": false,
      "logins_count": 0,
      "name": "manager@udacoffeeshop.com",
      "nickname": "manager",
      "picture": "https://s.gravatar.com/avatar/5bd3fbf085699285359fbe69e4f3d705?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
      "updated_at": "2020-04-20T16:12:22.415Z",
      "user_id": "auth0|5e9a3abb152a670c21497258"
    }
}
```
##### GET '/users/{user_id}'

- Get a user with the id provided in the URI.
- Request Arguments: None
- Requires permissions: `manage:barista` and/or `manage:manager`
- Returns: An object with a success key, and the requested user.

```json
{
  "success": true,
  "users": [
    {
      "created_at": "2020-04-17T23:24:43.499Z",
      "email": "manager@udacoffeeshop.com",
      "email_verified": false,
      "identities": [
        {
          "connection": "Username-Password-Authentication",
          "isSocial": false,
          "provider": "auth0",
          "user_id": "5e9a3abb152a670c21497258"
        }
      ],
      "last_ip": "41.249.52.37",
      "last_login": "2020-04-20T16:12:22.415Z",
      "logins_count": 4,
      "multifactor": [
        "guardian"
      ],
      "multifactor_last_modified": "2020-04-17T23:25:50.934Z",
      "name": "manager@udacoffeeshop.com",
      "nickname": "manager",
      "picture": "https://s.gravatar.com/avatar/5bd3fbf085699285359fbe69e4f3d705?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
      "updated_at": "2020-04-20T16:12:22.415Z",
      "user_id": "auth0|5e9a3abb152a670c21497258"
    }
  ]
}
```

##### DELETE '/users/{user_id}'

- Deleted a user with the id provided in the URI.
- Request Arguments: None
- Requires permissions: `manage:barista` and/or `manage:manager`
- Returns: An object success and deleted key, the id of the deleted user.

```json
{
  "success": true,
  "deleted": "auth0|5e9a3abb152a670c21497258"
}
```

##### PATCH '/users/{user_id}'
- Modifies an existing user in the auth0 database.
- Request Arguments: 
    - email: String
    - name: String
    - nickname: String
    - picture: String
    - password: String
- Requires permissions: `manage:barista` and/or `manage:manager`
- Returns: An object with success, and the newly modified user.

```json
{
  "success": true,
  "users": [
    {
      "created_at": "2020-04-17T23:24:43.499Z",
      "email": "manager@udacoffeeshop.com",
      "email_verified": false,
      "logins_count": 0,
      "name": "manager@udacoffeeshop.com",
      "nickname": "manager",
      "picture": "https://s.gravatar.com/avatar/5bd3fbf085699285359fbe69e4f3d705?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
      "updated_at": "2020-04-20T16:12:22.415Z",
      "user_id": "auth0|5e9a3abb152a670c21497258"
    }
  ]
}
```

## Testing
To run the tests, open `udacity-fsnd-udaspicelatte.postman_collection.json` collection in Postman.

Then run it with the collection runner.