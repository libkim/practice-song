import requests

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tj_no = db.Column(db.Integer, nullable=True)
    kumyoung_no = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    singer = db.Column(db.String(100), nullable=False)
    memo = db.Column(db.String(10000), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    song_list =  Song.query.all()
    return render_template('Index.html', data=song_list)

@app.route('/search', methods=['POST'])
def search():
    search_by = request.form['search_by']
    query = request.form['query']

    if search_by == 'singer':
        rjson1 = requests.get(f"https://api.manana.kr/karaoke/singer/{query}/tj.json").json()
        rjson2 = requests.get(f"https://api.manana.kr/karaoke/singer/{query}/kumyoung.json").json()
    else:
        rjson1 = requests.get(f"https://api.manana.kr/karaoke/song/{query}/tj.json").json()
        rjson2 = requests.get(f"https://api.manana.kr/karaoke/song/{query}/kumyoung.json").json()

    for r in rjson1:
        filtered_rjson2 = list(filter(lambda r2 : r2['title'].replace(" ", "") == r['title'].replace(" ", "") and r2['singer'].replace(" ", "") == r['singer'].replace(" ", ""), rjson2))
        
        if filtered_rjson2:
            r2 = filtered_rjson2[0]
            r['kumyoung_no'] = r2['no']
            r['title'] = r2['title']
            r['singer'] = r2['singer']
        else:
            r['kumyoung_no'] = '없음'
        
        r['tj_no'] = r.pop('no')
        del r['brand']
        del r['composer']
        del r['lyricist']
        del r['release']

    context = {
        "search_results": rjson1
    }

    return jsonify(context)

@app.route('/add', methods=['POST'])
def add():
    tj_no_receive = request.form['tj_no']
    kumyoung_no_receive = request.form['kumyoung_no']
    title_receive = request.form['title']
    singer_receive = request.form['singer']
    memo_receive = request.form['memo']

    song = Song(tj_no=tj_no_receive, kumyoung_no=kumyoung_no_receive, title=title_receive, singer=singer_receive, memo=memo_receive)
    db.session.add(song)
    db.session.commit()

    return jsonify()

@app.route('/inquire', methods=['POST'])
def inquire():
    id_receive = request.form['id']
    song = Song.query.filter_by(id=id_receive).first()

    context = {
        "id": song.id,
        "tj_no": song.tj_no,
        "kumyoung_no": song.kumyoung_no,
        "title": song.title,
        "singer": song.singer,
        "memo": song.memo
    }

    return jsonify(context)

@app.route('/update', methods=['POST'])
def update():
    id_receive = request.form['id']
    tj_no_receive = request.form['tj_no']
    kumyoung_no_receive = request.form['kumyoung_no']
    title_receive = request.form['title']
    singer_receive = request.form['singer']
    memo_receive = request.form['memo']

    song = Song.query.filter_by(id=id_receive).first()
    song.tj_no = tj_no_receive
    song.kumyoung_no = kumyoung_no_receive
    song.title = title_receive
    song.singer = singer_receive
    song.memo = memo_receive

    db.session.add(song)
    db.session.commit()

    return jsonify()

@app.route('/delete', methods=['POST'])
def delete():
    id_receive = request.form['id']
    song = Song.query.filter_by(id=id_receive).first()
    db.session.delete(song)
    db.session.commit()

    return jsonify()

if __name__ == "__main__":
    app.run(debug=True)
