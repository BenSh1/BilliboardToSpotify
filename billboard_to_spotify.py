import tkinter as tk
from tkinter import messagebox, ttk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ────────────────────────────────────────────────────────────────────────────────
# ▶ Spotify Developer credentials (from environment variables)
# ────────────────────────────────────────────────────────────────────────────────
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# ────────────────────────────────────────────────────────────────────────────────
# ▶  Spotify helper: returns an authenticated Spotipy client
# ────────────────────────────────────────────────────────────────────────────────

def get_spotify_client():
    scope = "playlist-modify-public"
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=scope,
            open_browser=True,
        )
    )

# ────────────────────────────────────────────────────────────────────────────────
# ▶  Scrape the Billboard Hot‑100 for a given date (YYYY‑MM‑DD → list[str])
# ────────────────────────────────────────────────────────────────────────────────

def scrape_billboard(date: str) -> list[str]:
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # Grab every <h3> that looks like a song title (uses both core classes)
    song_tags = soup.find_all(
        "h3",
        class_=lambda c: c and "c-title" in c and "a-no-trucate" in c,
    )
    return [tag.get_text(strip=True) for tag in song_tags]

# ────────────────────────────────────────────────────────────────────────────────
# ▶  Create playlist + add songs, returns playlist share‑link
# ────────────────────────────────────────────────────────────────────────────────

def create_playlist(sp: spotipy.Spotify, user_id: str, date: str, songs: list[str]) -> str:
    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"Billboard Top 100 • {date}",
        public=True,
        description=f"Billboard Hot‑100 songs for {date}",
    )
    playlist_id = playlist["id"]

    uris: list[str] = []
    for song in songs:
        result = sp.search(q=song, type="track", limit=1)
        items = result["tracks"]["items"]
        if items:
            uris.append(items[0]["uri"])

    # Add in chunks of 100 (API limit per call)
    if uris:
        sp.playlist_add_items(playlist_id, uris)
    return playlist["external_urls"]["spotify"]

# ────────────────────────────────────────────────────────────────────────────────
# ▶  Tkinter GUI
# ────────────────────────────────────────────────────────────────────────────────

class BillboardApp(ttk.Frame):
    SPOTIFY_GREEN = "#1DB954"
    SPOTIFY_DARK = "#191414"

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        master.title("Billboard → Spotify Playlist Builder")
        master.geometry("460x220")
        master.configure(bg=self.SPOTIFY_DARK)
        master.resizable(False, False)

        # ttk theme + custom styles
        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure(
            "TLabel",
            background=self.SPOTIFY_DARK,
            foreground="white",
            font=("Helvetica", 12, "bold"),
        )
        style.configure(
            "TEntry",
            fieldbackground="#121212",
            foreground="white",
            bordercolor=self.SPOTIFY_GREEN,
            padding=6,
            font=("Helvetica", 11),
        )
        style.configure(
            "Accent.TButton",
            background=self.SPOTIFY_GREEN,
            foreground=self.SPOTIFY_DARK,
            font=("Helvetica", 12, "bold"),
            padding=6,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#1ed760"), ("pressed", "#169f48")],
        )

        # Widgets
        ttk.Label(
            master,
            text="Enter a date (YYYY‑MM‑DD)",
        ).pack(pady=(25, 8))

        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(master, textvariable=self.date_var, width=30)
        self.date_entry.pack()
        self.date_entry.focus()

        ttk.Button(
            master,
            text="Create Playlist",
            command=self.run,
            style="Accent.TButton",
        ).pack(pady=20)

        ttk.Label(
            master,
            text="© Billboard to Spotify • OAuth required",
            font=("Helvetica", 8),
            foreground="#888",
        ).pack(side="bottom", pady=4)

    # ────────────────────────────────
    #  Main callback
    # ────────────────────────────────
    def run(self):
        date = self.date_var.get().strip()
        if not date:
            messagebox.showwarning("Input Required", "Please enter a date in YYYY‑MM‑DD format.")
            return
        try:
            self.master.config(cursor="wait")
            self.master.update()

            sp = get_spotify_client()
            user_id = sp.current_user()["id"]

            songs = scrape_billboard(date)
            if not songs:
                raise ValueError("No songs found. Double‑check the date format or chart availability.")

            playlist_link = create_playlist(sp, user_id, date, songs)
            messagebox.showinfo("Success", f"Playlist created!\n{playlist_link}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
        finally:
            self.master.config(cursor="")

# ────────────────────────────────────────────────────────────────────────────────
# ▶  Run the app
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    BillboardApp(root)
    root.mainloop()






