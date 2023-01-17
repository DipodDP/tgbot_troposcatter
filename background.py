import subprocess
from subprocess import Popen

from flask import Flask, redirect, url_for

app = Flask(__name__)

# process: Popen | None = None // get error on Pythonanywhere
process: Popen = None


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
        process = subprocess.Popen(["python", "bot.py"])  # add parameter shell=True if using venv
        print('Starting...')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
