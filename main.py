import requests
from bs4 import BeautifulSoup
from firebase import firebase
from flask import Flask, json, request
from flask import render_template

app = Flask(__name__)
firebaseApp = firebase.FirebaseApplication('https://letzteleben-398ef.firebaseio.com/', None)


class Game:
    def __init__(self, name, id, description, url):
        self.name = name
        self.id = id
        self.description = description
        self.url = url


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
            # find max existing id in firebase and set +1 to the new element
            i = 0
            for item in firebase_get_games():
                if item['id'] > i:
                    i = item['id']
            game = Game(request.form['game-title'], i + 1, request.form['game-description'],
                        request.form['game-image-url'])
            firebase_add_game(game)
            return render_template('games.html', content=firebase_get_games())
        else:
            return {'id': 10000}, 200


@app.route('/games/<int:game_id>', methods=['GET', 'POST', 'DELETE'])
def get_game_by_id(game_id):
    content = firebaseApp.get('/games/' + str(game_id), None)
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        if request.method == 'GET':
            submission_successful = True
            return render_template("games.html", content=firebase_get_games(), game=temp_json,
                                   submission_successful=submission_successful)
        elif request.method == 'POST':
            # Update game record
            if request.form['edit_game'] == 'Edit':
                # TODO Receive data from frontend
                game = Game("new game", 11, "smgameCHANGED",
                            "data:image/jpeg;base64,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")
                firebase_add_game(game)
            return render_template('games.html', content=firebase_get_games())
        elif request.method == 'DELETE':
            firebase_delete_game(game_id)
            # TODO update page after deleting item
            return render_template('games.html', content=firebase_get_games())
    else:
        return "No data about this game"


@app.route('/scrape')
def scrape():
    # Collect first page of games’ list (Collecting and Parsing data)
    page = requests.get(
        'https://web.archive.org/web/20201001124341/https://www.metacritic.com/browse/games/score/metascore/all/pc/filtered')

    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # Pull all text from the clamp-image-wrap
    games_image_name_list = soup.find_all(class_='clamp-image-wrap')

    # Remove img tags for class mcmust
    must_links = soup.find_all(class_='mcmust')
    for link in must_links:
        link.decompose()

    # Pull src and alt from all instances of img tag
    games_image_list_items = []
    games_name_list_items = []
    for item in games_image_name_list:
        for img in item.find_all('img'):
            games_image_list_items.append(img.get('src'))
            games_name_list_items.append(img.get('alt'))

    # Pull all text from the summary
    games_desc_list = soup.find_all(class_='summary')
    games_desc_list_items = []
    for item in games_desc_list:
        games_desc_list_items.append(item.get_text())

    result = ''
    for i in range(0, len(games_image_list_items), 1):
        result += '\n\t' + games_name_list_items[i] + '\n' + games_image_list_items[i] + '\n' + games_desc_list_items[i]
    return result


def firebase_get_games():
    content = firebaseApp.get('/games', None)
    array = []
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        for item in temp_json:
            if item is not None:
                array.append(temp_json[item])
    return array


def firebase_add_game(game: Game):
    result = firebaseApp.patch('/games/' + str(game.id),
                               data={'description': game.description, 'id': game.id, 'name': game.name,
                                     'url': game.url})
    return result


def firebase_delete_game(game_id):
    firebaseApp.delete('/games', game_id)
    return ""


if __name__ == "__main__":
    app.config.update(TEMPLATES_AUTO_RELOAD=True)
    app.run()
