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


@app.route('/games/<int:game_id>')
def get_game_by_id(game_id):
    content = firebaseApp.get('/games/' + str(game_id), None)
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        submission_successful = True
        return render_template("games.html", content=allGames, game=temp_json,
                               submission_successful=submission_successful)
    else:
        return "No data about this game"


def firebase_get_games():
    content = firebaseApp.get('/games', None)
    array = []
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        for item in temp_json:
            array.append(temp_json[item])
    return array


allGames = firebase_get_games()

if __name__ == "__main__":
    app.run()
