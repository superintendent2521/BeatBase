from flask import Flask, render_template, jsonify, request, send_file
import json
import os
import random
import time
import threading

app = Flask(__name__)

# Load music data from JSON file
music_data = json.load(open('music.json'))

# Create a dictionary to store the current song being streamed
current_song = {}

# Create a lock to synchronize access to the current song
song_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html', music=music_data)

@app.route('/stream', methods=['GET'])
def stream_song():
    # Get the song ID from the query string
    song_id = request.args.get('song_id')
    if song_id:
        # Find the song in the music data
        song = next((song for song in music_data if song['id'] == song_id), None)
        if song:
            # Return the song data as JSON
            return jsonify({'song': song})
    return jsonify({'error': 'Song not found'}), 404

@app.route('/stream/live', methods=['GET'])
def live_stream():
    # Return a live stream of the current song
    global current_song
    with song_lock:
        if not current_song:
            # Choose a random song from the /music folder
            music_folder = 'music'
            songs = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
            song_file = random.choice(songs)
            current_song = {'title': song_file, 'file': os.path.join(music_folder, song_file)}

        return send_file(current_song['file'], mimetype='audio/mpeg')

@app.route('/stream/now_playing', methods=['GET'])
def now_playing():
    # Return the currently playing song
    global current_song
    with song_lock:
        return jsonify({'now_playing': current_song.get('title')})

@app.route('/stream/next', methods=['GET'])
def next_song():
    # Play the next song
    global current_song
    with song_lock:
        current_song = {}
    return jsonify({'message': 'Next song loading...'})

def play_song_in_background():
    while True:
        time.sleep(10)  # simulate a delay between songs
        global current_song
        with song_lock:
            if not current_song:
                next_song()

# Start playing songs in the background
threading.Thread(target=play_song_in_background).start()

if __name__ == '__main__':
    app.run(debug=True)
