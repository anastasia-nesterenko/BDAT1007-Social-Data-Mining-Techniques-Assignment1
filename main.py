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
        # Update game record
        elif request.method == 'POST':
            game_json = request.get_json()
            game = Game(game_json['name'], game_id, game_json['description'], game_json['url'])
            firebase_add_game(game)
            return render_template('games.html', content=firebase_get_games())
        elif request.method == 'DELETE':
            firebase_delete_game(game_id)
            return render_template('games.html', content=firebase_get_games())
    else:
        return "No data about this game"


@app.route('/scrape')
def scrape():
    web_scrape_result = web_scrape()
    for game in web_scrape_result:
        firebase_add_game(game)
    return {'status': "uploaded scrapped games to firebase DB"}, 200


def firebase_get_games():
    content = firebaseApp.get('/games', None)
    array = []
    if content is not None:
        temp_serialized = json.dumps(content)
        temp_json = json.loads(temp_serialized)
        for item in temp_json:
            if item is not None:
                array.append(item)
    return array


# Add or update existing record
def firebase_add_game(game: Game):
    result = firebaseApp.patch('/games/' + str(game.id),
                               data={'description': game.description, 'id': game.id, 'name': game.name,
                                     'url': game.url})
    return result


def firebase_delete_game(game_id):
    firebaseApp.delete('/games', game_id)
    return ""


def web_scrape():
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
        games_desc_list_items.append(item.get_text().strip())

    result_array = []
    for i in range(0, len(games_image_list_items), 1):
        game = Game(games_name_list_items[i], i + 1, games_desc_list_items[i], games_image_list_items[i])
        result_array.append(game)
    return result_array


if __name__ == "__main__":
    app.config.update(TEMPLATES_AUTO_RELOAD=True)
    app.run()
