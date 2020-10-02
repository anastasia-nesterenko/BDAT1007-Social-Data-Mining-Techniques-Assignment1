from firebase import firebase
from flask import Flask, json, request
from flask import render_template

app = Flask(__name__)
firebaseApp = firebase.FirebaseApplication('https://letzteleben-398ef.firebaseio.com/', None)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/games', methods=['GET', 'POST'])
def games():
    if request.method == 'GET':
        return render_template('games.html', content=firebase_get_games())
    elif request.method == 'POST':
        if request.form['add_game'] == 'Add':
            # TODO Add game to firebase
            return render_template('games.html', content=firebase_get_games())
        else:
            return {'id': 10000}, 200


@app.route('/games/<int:game_id>', methods=['GET', 'DELETE'])
def get_game_by_id(game_id):
    content = firebaseApp.get('/games/' + str(game_id), None)
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        if request.method == 'GET':
            submission_successful = True
            return render_template("games.html", content=firebase_get_games(), game=temp_json,
                                   submission_successful=submission_successful)
        elif request.method == 'DELETE':
            # TODO Delete game
            return {'id': game_id, 'status': 'was deleted'}, 200
    else:
        return "No data about this game"


def firebase_get_games():
    content = firebaseApp.get('/games', None)
    array = []
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        for item in temp_json:
            array.append(item)
    return array


if __name__ == "__main__":
    app.run()
