import subprocess, sys
from subprocess import Popen

from flask import Flask, redirect, url_for

app = Flask(__name__)

process: Popen | None = None


@app.route('/')
def home():
    global process
    if process:
        status = process.poll()
        if status is None:
            result = 'alive! :)'
        else:
            result = f'stopped with code {status}.  Press <a href="/start">Start</a>'
    else:
        result = 'down! :(. Press <a href="/start">Start</a>'
    return f'Bot is {result}'


@app.route('/start')
def start():
    global process
    status = 'Down'
    if process:
        status = process.poll()
    if status is not None:
        process = subprocess.Popen([sys.executable, "bot.py"])
        print('Starting...')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
