# Billboard to Spotify 🎵

This app lets you create a Spotify playlist from the Billboard Hot 100 chart on any date you choose.

## ✅ How to Run

1. Clone this repo:
git clone https://github.com/yourusername/BillboardToSpotify cd BillboardToSpotify


2. Install requirements:
pip install -r requirements.txt


3. Create a `.env` file in the root folder with:
SPOTIPY_CLIENT_ID=your_spotify_client_id 
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret 
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

4. Run the app:
python billboard_to_spotify.py

## 🛠️ Prerequisites

- Spotify Developer account
- A registered Spotify App (free)
- Python 3.9+