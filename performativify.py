# performativify.py
import os, argparse, math, datetime as dt
from collections import Counter
from dotenv import load_dotenv
import logging, warnings
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# silence spotipy logs
for name in ("spotipy", "spotipy.client"):
    logging.getLogger(name).setLevel(logging.CRITICAL)
    logging.getLogger(name).propagate = False
warnings.filterwarnings("ignore", module="spotipy")

load_dotenv()
SCOPES = "user-top-read"

def get_sp(client_id=None, client_secret=None, redirect_uri=None):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPES,
        client_id=client_id or os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=client_secret or os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=redirect_uri or os.getenv("SPOTIPY_REDIRECT_URI"),
        open_browser=True
    ))

def clamp01(x): return max(0.0, min(1.0, x))
def pct(x): return int(round(100.0 * clamp01(x)))
def bar(x, width=20):
    n = int(round(clamp01(x) * width))
    return "[" + "#" * n + "-" * (width - n) + "]"

def fetch_top(sp, time_range="short_term", limit=30):
    items = sp.current_user_top_tracks(time_range=time_range, limit=limit).get("items", [])
    tracks = []
    for t in items:
        if not t or not t.get("id"): continue
        album = t.get("album", {})
        tracks.append({
            "id": t["id"],
            "name": t["name"],
            "artists": [a["name"] for a in t.get("artists", [])],
            "primary_artist_id": t["artists"][0]["id"],
            "explicit": 1 if t.get("explicit") else 0,
            "popularity": t.get("popularity", 0),
            "release_date": album.get("release_date"),
            "markets": len(album.get("available_markets", [])),
            "preview": 1 if t.get("preview_url") else 0,
            # skip audio-features entirely to avoid 403/logs
            "danceability": None, "energy": None, "valence": None, "acousticness": None,
        })
    return tracks

def fetch_artists(sp, track_items):
    ids = [t["primary_artist_id"] for t in track_items]
    uniq = list(dict.fromkeys(ids))
    artists = []
    for i in range(0, len(uniq), 50):
        artists.extend(sp.artists(uniq[i:i+50])["artists"])
    return artists

def shannon_entropy(counts):
    total = float(sum(counts))
    if total == 0 or len(counts) <= 1: return 0.0
    import math
    h = 0.0
    for c in counts:
        p = c / total
        h -= p * math.log(p + 1e-12, 2)
    return h / math.log(len(counts), 2)

def herfindahl(proportions): return sum(p*p for p in proportions)

def months_since(dstr):
    if not dstr: return None
    try:
        parts = dstr.split("-")
        if len(parts) == 1: y, m, d = int(parts[0]), 1, 1
        elif len(parts) == 2: y, m, d = int(parts[0]), int(parts[1]), 1
        else: y, m, d = map(int, parts[:3])
        then = dt.date(y, m, d); today = dt.date.today()
        return (today.year - then.year) * 12 + (today.month - then.month)
    except Exception:
        return None

def _avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs)/len(xs) if xs else None

def metrics(tracks, artists):
    if not tracks: return {}
    import math

    pop = _avg([t["popularity"]/100.0 for t in tracks]) or 0.0
    explicit = _avg([t["explicit"] for t in tracks]) or 0.0
    recency = _avg([max(0.0, 1.0 - min(120, months_since(t["release_date"])) / 120.0)
                    if months_since(t["release_date"]) is not None else None for t in tracks]) or 0.0
    globalness = _avg([min(1.0, (t["markets"] or 0)/200.0) for t in tracks]) or 0.0
    

    a_pop = _avg([a.get("popularity", 0)/100.0 for a in artists]) or 0.0
    a_follow = _avg([math.log10(1 + a.get("followers", {}).get("total", 0))/7.0 for a in artists]) or 0.0
    genres = []
    for a in artists: genres.extend(a.get("genres", []))
    genre_variety = shannon_entropy(Counter(genres).values())

    primary_ids = [t["primary_artist_id"] for t in tracks]
    proportions = [c/float(len(tracks)) for c in Counter(primary_ids).values()]
    artist_diversity = 1.0 - herfindahl(proportions)
    artist_mainstream = clamp01(0.7*a_pop + 0.3*a_follow)
    artist_niche = (sum(1 for a in artists if a.get("popularity", 0) < 40) / float(len(artists))) if artists else 0.0

    # fallback scoring (no features)
    score = (0.28*pop + 0.12*explicit + 0.14*recency + 0.10*globalness
         + 0.17*genre_variety + 0.13*artist_diversity + 0.06*artist_mainstream)


    return {
        "score": clamp01(score), "have_features": False,
        "pop": pop, "explicit": explicit,
        "recency": recency, "globalness": globalness,
        "genre_variety": genre_variety, "artist_diversity": artist_diversity,
        "artist_mainstream": artist_mainstream, "artist_niche": artist_niche,
        "unique_genres": len(set(genres)), "unique_artists": len(artists),
        "dance": None, "energy": None, "valence": None, "acoustic": None,
    }

def suggestions(m):
    tips = []
    if m["artist_diversity"] < 0.65: tips.append("Rotate in more artists to avoid monoculture vibes.")
    if m["artist_mainstream"] < 0.5: tips.append("Add a couple of big-name artists for social flex.")
    if m["artist_niche"] < 0.3: tips.append("Slip in a few low-pop indie names for ‘I knew them early’.")
    if m["genre_variety"] < 0.5: tips.append("Widen your genre net to look intentionally curated.")
    if not tips: tips.append("You’re already delightfully performative. Maintain the illusion.")
    return tips

def main():
    ap = argparse.ArgumentParser(description="Silly Spotify Performativify")
    ap.add_argument("--time_range", default="short_term", choices=["short_term","medium_term","long_term"])
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    sp = get_sp()
    tracks = fetch_top(sp, args.time_range, args.limit)
    if not tracks: print("No tracks found. Play more music."); return
    artists = fetch_artists(sp, tracks)
    m = metrics(tracks, artists)

    print("=== Performativify ===")

    print("Time range: {}".format({"short_term": "short term (~last 4 weeks)", "medium_term": "medium term (~last 6 months)", "long_term": "long term (~several years)"}.get(args.time_range, args.time_range.replace("_"," "))))
    print("Tracks analyzed: {}".format(len(tracks)))
    print("")
    print("Overall Performative Score: {} / 100 {}".format(pct(m["score"]), bar(m["score"])))
    print("")
    print("Mainstream Flex (popularity): {:>3}% {}".format(pct(m["pop"]), bar(m["pop"])))
    print("Recency (newness):            {:>3}% {}".format(pct(m["recency"]), bar(m["recency"])))
    print("Globalness (markets):         {:>3}% {}".format(pct(m["globalness"]), bar(m["globalness"])))
    print("Edgy Points (explicit):       {:>3}% {}".format(pct(m["explicit"]), bar(m["explicit"])))
    print("Artist Mainstream:            {:>3}% {}".format(pct(m["artist_mainstream"]), bar(m["artist_mainstream"])))
    print("Artist Diversity:             {:>3}% {}".format(pct(m["artist_diversity"]), bar(m["artist_diversity"])))
    print("Genre Variety (artists):      {:>3}% {}".format(pct(m["genre_variety"]), bar(m["genre_variety"])))
    print("")
    print("Unique artists: {}".format(m["unique_artists"]))
    print("Unique genres:  {}".format(m["unique_genres"]))
    print("")
    print("How to be more performative:")
    for i, tip in enumerate(suggestions(m), 1):
        print("{}. {}".format(i, tip))

if __name__ == "__main__":
    main()
