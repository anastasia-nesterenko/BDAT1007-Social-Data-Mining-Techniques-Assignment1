from firebase import firebase
from flask import Flask, json
from flask import render_template

app = Flask(__name__)
firebaseApp = firebase.FirebaseApplication('https://letzteleben-398ef.firebaseio.com/', None)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/games')
def get_games():
    content = firebaseApp.get('/games', None)
    array = []
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        for item in temp_json:
            array.append(temp_json[item])

        return render_template('games.html', content=array)
    else:
        return render_template('games.html')


@app.route('/games/<int:game_id>')
def get_game_by_id(game_id):
    content = firebaseApp.get('/games/' + str(game_id), None)
    if content is not None:
        return content
    else:
        return "No data about this game"


if __name__ == "__main__":
    app.run()
