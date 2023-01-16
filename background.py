import subprocess
from subprocess import Popen

from flask import Flask, redirect, url_for

app = Flask('__name__')

process: Popen | None = None


@app.route('/')
def home():
    global process
    if process:
        status = process.poll()
        if status is None:
            result = 'alive! :)'
        else:
            result = status
    else:
        result = 'down! :(. Press <a href="/start">Start</a>'
    return f'Bot is {result}'


@app.route('/start')
def start():
    global process
    if process is None:
        process = subprocess.Popen(["python", "bot.py"], shell=True)
        print('Starting...')
    print(process.poll())

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
