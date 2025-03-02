from flask import Flask, render_template, request, redirect, url_for, session
from flask_babel import Babel

app = Flask(__name__)
app.config.from_pyfile('config.py')

babel = Babel(app)

LANGUAGES = ['en', 'hi', 'ta', 'te', 'bn', 'mr']

def get_locale():
    return session.get('language', 'en')

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    return {'get_locale': get_locale}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/change_language/<lang>')
def change_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
