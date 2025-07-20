from flask import Flask, redirect, request, render_template
import requests

app = Flask(__name__)
app.secret_key = 'något-hemligt'

# Spotify API-uppgifter
CLIENT_ID = '1a01972cabac4f309c2f1968b05d908e'
CLIENT_SECRET = '11728f25c7994139bd8ac76f6eaa22ce'
REDIRECT_URI = 'https://255b38293ee0.ngrok-free.app/callback'  # BYT till din riktiga ngrok-länk!
SCOPE = 'user-top-read user-read-recently-played'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = (
        'https://accounts.spotify.com/authorize?'
        f'client_id={CLIENT_ID}&response_type=code'
        f'&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog=true'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')

    # Hämta access token
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    response_data = response.json()
    access_token = response_data.get('access_token')

    headers = {'Authorization': f'Bearer {access_token}'}

    # Hämta topplåtar
    top_tracks_data = requests.get(
        'https://api.spotify.com/v1/me/top/tracks?limit=10',
        headers=headers
    ).json()

    top_tracks = [track['name'] for track in top_tracks_data.get('items', [])]

    return render_template('results.html', tracks=top_tracks)

if __name__ == '__main__':
    app.run()

