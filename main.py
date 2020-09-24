from firebase import firebase
from flask import Flask
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
def get_orders():
    content = firebaseApp.get('/games', None)
    if content is not None:
        return render_template('games.html', content=content)
    else:
        return render_template('games.html')


@app.route('/games/<int:game_id>')
def get_order_by_id(game_id):
    content = firebaseApp.get('/games/' + str(game_id), None)
    if content is not None:
        return content
    else:
        return "No data about this game"


if __name__ == "__main__":
    app.run()
