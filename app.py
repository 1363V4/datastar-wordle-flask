import os
import mimetypes
import re
import time
from random import choice
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.logger import logger
from datastar_py.sse import ServerSentEventGenerator as SSE
from tinydb import TinyDB, table
from words import words


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

# Configure MIME types for JavaScript
mimetypes.add_type('application/javascript', '.js')

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1 per second", "1000 per day"],
    storage_uri="memory://",
)

db = TinyDB("data.json", sort_keys=True, indent=2)
games = db.table('games')

def get_colors(word, attempt):
    result = ['B'] * len(attempt)    
    remaining = {}
    for char in word:
        remaining[char] = remaining.get(char, 0) + 1
    for i, (w_char, a_char) in enumerate(zip(word, attempt)):
        if w_char == a_char:
            result[i] = 'G'
            remaining[w_char] -= 1
    for i, a_char in enumerate(attempt):
        if result[i] != 'G' and a_char in remaining and remaining[a_char] > 0:
            result[i] = 'Y'
            remaining[a_char] -= 1
    return ''.join(result)

def view_function(data):
    no_tries = data['no_tries']
    no_letters = data['no_letters']
    attempts = data['attempts']
    status = data['status']
    match status:
        case "won":
            overlay = f'''
            <div class="gc overlay">
            <p class="gt l">A WINNER IS YOU</p>
            <p>In only {len(attempts)} attempts, wow :o</p>
            <a href="/new_game"><div class="gc difficulty-button">Play again?</div></a>
            </div>
            '''
        case "lost":
            overlay = f'''
            <div class="gc overlay">
            <p class="gt l">NICE TRY...</p>
            <p>The word was {data['word']}</p>
            <a href="/new_game"><div class="gc difficulty-button">Play again?</div></a>
            </div>
            '''
        case _:
            overlay = ""
    html = f'''
    <main 
    id="main" 
    class="gz"
    data-on-wordle="@post('/attempt/' + evt.detail.value)"
    data-indicator-fetching
    >
    {overlay}
    <img src="/static/svg/gooey-balls.svg" class="gc" data-show="$fetching">
    <div
    class="gc wordle-wrapper"
    style="grid-template-rows: repeat({no_tries}, 1fr); gap: .2rem"
    >
    '''
    for attempt in attempts:
        html += f'<div class="line" style="grid-template-columns: repeat({no_letters}, 1fr)">'
        delay = 0
        for letter, color in zip(attempt['letters'], attempt['colors']):
            bg_color = {'G': "green", 'Y': "chocolate", 'B': "black"}.get(color)
            html += f'''
            <div class="square"
            completed
            data-delay="{delay}s"
            style="background: {bg_color}">
            {letter}
            </div>'''
            delay += 2 / no_tries
        html += '</div>'
    if no_tries != len(attempts):
        html += f'''
        <wordle-line length='{no_letters}'></wordle-line>
        '''
    for _ in range(no_tries - len(attempts) - 1):
        html += f'<div class="line" style="grid-template-columns: repeat({no_letters}, 1fr)">'
        for _ in range(no_letters):
            html += f'<div class="square"></div>'
        html += '</div>'
    html += '''
    </div>
    </main>
    '''
    return html

@app.before_request
def before_request():
    if not session.get('db_id'): 
        redirect(url_for("index"))

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/difficulty/<difficulty>')
def difficulty(difficulty):
    match difficulty:
        case "easy":
            word = choice(words[5])
            no_tries = 7
            no_letters = 5
        case "medium":
            word = choice(words[5])
            no_tries = 6
            no_letters = 5
        case "hard":
            word = choice(words[6])
            no_tries = 5
            no_letters = 6
        case "hackerman":
            word = choice(words[9])
            no_tries = 1
            no_letters = 9
        case _:
            # Default to easy difficulty
            word = choice(words[5])
            no_tries = 7
            no_letters = 5
    data = {
        'word': word,
        'no_tries': no_tries,
        'no_letters': no_letters,
        'attempts': [],
        'status': "running"
    }
    db_id = int(time.time() * 1000)
    games.insert(table.Document(data, doc_id=db_id))
    session['db_id'] = db_id
    html = view_function(data)
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)

@app.post('/attempt/<details>')
def attempt(details):
    db_id = session['db_id']
    data = games.get(doc_id=db_id)
    if data is None:
        return "", 404
    if re.match(r'^[A-Z]+$', details) and len(details) == data['no_letters']:
        word = data['word']
        colors = get_colors(word, details)
        attempts = data['attempts']
        attempts += [{'letters': details, 'colors': colors}]
        games.update({'attempts': attempts}, doc_ids=[db_id])
        if details == word:
            games.update({'status': "won"}, doc_ids=[db_id])
        elif len(attempts) == data['no_tries']:
            games.update({'status': "lost"}, doc_ids=[db_id])
        data = games.get(doc_id=db_id)
        html = view_function(data)
        return SSE.merge_fragments(fragments=[html])
    return "", 204

@app.get('/new_game')
def new_game():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    logger.debug("Debug mode started")
    app.run(debug=True)
