from flask import Flask, render_template, request
import spotify_query

app = Flask(__name__)
last_query_result = []


@app.get('/player')
def player():
    track_id = request.args.get('track_id')
    print(last_query_result)
    return render_template('index.html', query_results=last_query_result, spotify_embedding=get_spotify_embedding(track_id))


@app.post('/query')
def query():
    q = request.form['query']
    last_query_result = spotify_query.search(q)
    return render_template('index.html', query_results=last_query_result)


@app.route('/')
def hello():
    return render_template('index.html')


def get_spotify_embedding(id):
    spotify_embedding = f""" 
        <iframe style="border-radius:12px" 
        src="https://open.spotify.com/embed/track/{id}" width="20%" height="80" frameBorder="0" allowfullscreen=""
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
        </iframe> 
    """
    return spotify_embedding


app.run(debug=True)
