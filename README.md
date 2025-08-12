# Performativify

A silly script to analyze your Spotify listening habits and tell you how "performative" your taste is. Ever wondered if your music choices truly reflect a curated, sophisticated persona, or just... you? This tool gives you a score!

## How it Works

`performativify.py` connects to your Spotify account, fetches your top tracks, and analyzes various metrics to calculate an "Overall Performative Score." It looks at:

*   **Mainstream Flex (popularity):** How popular are the tracks you listen to?
*   **Recency (newness):** Are you listening to newly released music?
*   **Globalness (markets):** How widely available is the music you listen to?
*   **Edgy Points (explicit):** How much explicit content is in your top tracks?
*   **Artist Mainstream:** How popular and followed are your top artists?
*   **Artist Diversity:** How varied are the artists in your top tracks?
*   **Genre Variety:** How many different genres do your top artists cover?

Based on these, it provides a score and some tongue-in-cheek suggestions on how to enhance your performative musical persona.

## Setup

1.  **Python:** Ensure you have Python 3.x installed.

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Spotify API Credentials:**
    To use this script, you need to create a Spotify Developer application to get your API credentials.
    *   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    *   Log in with your Spotify account.
    *   Click "Create an app".
    *   Fill in the details (App Name, App Description). You can use anything for these.
    *   Once created, you will see your **Client ID** and **Client Secret**.
    *   Click "Edit Settings" for your app.
    *   Under "Redirect URIs", add `http://localhost:8888/callback`. This is crucial for the authentication flow.
    *   Save the settings.

4.  **Create a `.env` file:**
    In the same directory as `performativify.py`, create a file named `.env` and add your Spotify API credentials to it:

    ```
    SPOTIPY_CLIENT_ID='your_client_id_here'
    SPOTIPY_CLIENT_SECRET='your_client_secret_here'
    SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
    ```
    Replace `'your_client_id_here'` and `'your_client_secret_here'` with the actual values from your Spotify app.

## Usage

Run the script from your terminal:

```bash
python performativify.py
```

The first time you run it, a browser window will open asking you to authorize the application to access your Spotify data. After authorization, you'll be redirected to `http://localhost:8888/callback`, and the script will continue.

### Command-line Arguments

*   `--time_range`: Specifies the time frame for your top tracks.
    *   `short_term` (default): Approximately the last 4 weeks.
    *   `medium_term`: Approximately the last 6 months.
    *   `long_term`: Several years of listening history.
    *   Example: `python performativify.py --time_range long_term`

*   `--limit`: The number of top tracks to analyze (default: 30).
    *   Example: `python performativify.py --limit 50`

## Example Output

```
=== Performativify ===
Time range: short term (~last 4 weeks)
Tracks analyzed: 30

Overall Performative Score:  75 / 100 [###############-----]

Mainstream Flex (popularity):  80% [################----]
Recency (newness):             60% [############--------]
Globalness (markets):          90% [##################--]
Edgy Points (explicit):        20% [####----------------]
Artist Mainstream:             70% [##############------]
Artist Diversity:              55% [###########---------]
Genre Variety (artists):       65% [#############-------]

Unique artists: 25
Unique genres:  10

How to be more performative:
1. Rotate in more artists to avoid monoculture vibes.
2. Slip in a few low-pop indie names for ‘I knew them early’.
```

## Disclaimer

This script is purely for entertainment purposes and uses a subjective, humorous definition of "performative." It's not meant to be a serious judgment of your musical taste! Enjoy your music, however you listen to it.