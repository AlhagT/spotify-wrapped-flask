from flask import Flask, redirect, request, render_template, session
import requests

app = Flask(__name__)
app.secret_key = 'något-hemligt'

CLIENT_ID = '1a01972cabac4f309c2f1968b05d908e'
CLIENT_SECRET = '11728f25c7994139bd8ac76f6eaa22ce'
REDIRECT_URI = 'https://21a08ea3f81f.ngrok-free.app/callback'
SCOPE = 'user-top-read'

@app.route('/')
def index():
    return render_template('index.html')  # logga in-knapp


@app.route('/login')
def login():
    auth_url = (
        'https://accounts.spotify.com/authorize'
        f'?client_id={CLIENT_ID}&response_type=code'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope={SCOPE}&show_dialog=true'
    )
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    try:
        token_response = response.json()
    except ValueError:
        return f"Fel vid JSON-avkodning från Spotify: {response.text}", 500

    access_token = token_response.get('access_token')
    if not access_token:
        return f"Fel vid inloggning: {token_response}", 400

    session['access_token'] = access_token
    return redirect('/choose-period')



@app.route('/choose-period')
def choose_period():
    return render_template('choose_period.html')


@app.route('/wrapped')
def wrapped():
    period = request.args.get('period', 'long_term')
    access_token = session.get('access_token')

    if not access_token:
        return redirect('/')

    headers = {'Authorization': f'Bearer {access_token}'}

    # Hämta topp 50 låtar (endast låttitel)
    top_tracks_data = requests.get(
        f'https://api.spotify.com/v1/me/top/tracks?limit=50&time_range={period}',
        headers=headers
    ).json()

    top_tracks = [
        {'track': track['name'], 'full': f"{track['name']} – {track['artists'][0]['name']}"}
        for track in top_tracks_data.get('items', [])
    ]


    # Hämta topp 50 artister (endast artistnamn)
    top_artists_data = requests.get(
        f'https://api.spotify.com/v1/me/top/artists?limit=50&time_range={period}',
        headers=headers
    ).json()

    top_artists = [
        artist['name']
        for artist in top_artists_data.get('items', [])
    ]

    return render_template(
        'results.html',
        tracks=top_tracks,
        artists=top_artists,
        period=period
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

