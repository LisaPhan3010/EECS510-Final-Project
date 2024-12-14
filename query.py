from datetime import datetime
import re
import csv
from automaton import Automaton
# Song class to represent individual songs
class Song:
    def __init__(self, track_name, artist, released_year, released_month, released_day, streams, bpm, key, mode):
        #initializes playlist attributes
        self.track_name = track_name
        self.artist = artist
        self.released_year = int(released_year)
        self.released_month = int(released_month)
        self.released_day = int(released_day)
        self.streams = int(streams)
        self.bpm = int(bpm)
        self.key = key
        self.mode = mode
        self.released_date = datetime(self.released_year, self.released_month, self.released_day)

    def __str__(self):
        #demonstrates song object as a string
        return f"{self.track_name} by {self.artist} ({self.released_date.date()}) - Streams: {self.streams}, BPM: {self.bpm}, Key: {self.key}, Mode: {self.mode}"

class Playlist:
    def __init__(self):
        self.songs = [] #an empty list for storing songs

    def add_song(self, song):
        self.songs.append(song) #add songs to the playlist
    
    def query(self, sql_query):
        #match the query to extract selected attributes and conditions
        match = re.match(r"SELECT (.+) FROM playlist WHERE (.+)", sql_query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid query format")
        #pplit selected attributes by comma and strip any extra whitespace
        selected_attributes = match.group(1).split(',')
        selected_attributes = [attr.strip() for attr in selected_attributes]
        #extract condition
        conditions_str = match.group(2)
        conditions = self.parse_conditions(conditions_str)
        #filter songs
        result = []
        for song in self.songs: 
            if self.match_song(song, conditions):
                result.append({attr: getattr(song, attr) for attr in selected_attributes})
        return result

    #parse conditions from the query string to dictionary
    def parse_conditions(self, conditions_str):
        conditions = {}
        condition_parts = re.split(r" AND | OR ", conditions_str, flags=re.IGNORECASE)
        #determine operators and split key-value pairs
        for part in condition_parts:
            if ">=" in part:
                key, value = part.split(">=", 1)
                operator = ">="
            elif "<=" in part:
                key, value = part.split("<=", 1)
                operator = "<="
            elif ">" in part:
                key, value = part.split(">", 1)
                operator = ">"
            elif "<" in part:
                key, value = part.split("<", 1)
                operator = "<"
            elif "=" in part:
                key, value = part.split("=", 1)
                operator = "=="
            else:
                raise ValueError(f"Unsupported condition: {part}")

            key = key.strip()
            value = value.strip().strip("'")

            #convert numeric values to integers
            if value.isdigit():
                value = int(value)

            conditions[key] = (operator, value) #add condition to dictionary

        return conditions

    #check for matched songs according to the given conditions
    def match_song(self, song, conditions):
        for key, (operator, value) in conditions.items():
            song_value = getattr(song, key, None)

            #handle invalid key
            if song_value is None:
                return False

            # perform the comparison
            if not self.compare(song_value, value, operator):
                return False

        return True
    
    #compare song attributes based on operators
    def compare(self, song_value, condition_value, operator):
        if operator == "==":
            return song_value == condition_value
        elif operator == "!=":
            return song_value != condition_value
        elif operator == "<":
            return song_value < condition_value
        elif operator == "<=":
            return song_value <= condition_value
        elif operator == ">":
            return song_value > condition_value
        elif operator == ">=":
            return song_value >= condition_value
        return False

#check if the automaton accepts a given string
def accept(A,w):
    result = A.accepts(w)
    return result

def main():
    playlist = Playlist()

    #load songs from a CSV file
    try:
        with open("spotify-2023.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    #create a Song object for each row in the file
                    song = Song(
                        track_name=row["track_name"],
                        artist=row["artist"],
                        released_year=row["released_year"],
                        released_month=row["released_month"],
                        released_day=row["released_day"],
                        streams=row["streams"],
                        bpm=row["bpm"],
                        key=row["key"],
                        mode=row["mode"]
                    )
                    playlist.add_song(song)
                except ValueError as e:
                    print(f"Skipping song due to error: {e}")
    except FileNotFoundError:
        print("File not found. Ensure 'songs.csv' exists in the working directory.")
        return
    #automaton components
    states = {'start', 'select', 'attributes', 'from', 'playlist', 
              'where', 'condition', 'logical_op', 'accept'}
    inputs = {'SELECT', 'FROM', 'WHERE', 'AND', 'OR', '=', '>', '>=', '<', '<=', 'track_name', 'artist', 'released_year', 
              'released_month', 'released_day', 'streams', 'bpm', 'key', 'mode', 'value'}
    start_state = 'start'
    accept_states = {'accept'}
    transitions = {
        ('start', 'SELECT'): {'select'}, 
        ('select', 'track_name,'): {'select'}, 
        ('select', 'artist'): {'attributes'}, 
        ('attributes', 'FROM'): {'from'}, 
        ('from', 'playlist'): {'playlist'}, 
        ('playlist', 'WHERE'): {'where'}, 
        ('where', 'released_month'): {'condition'}, 
        ('condition', '='): {'logical_op'}, 
        ('logical_op', '12'): {'logical_op'}, 
        ('logical_op', 'AND'): {'where'}, 
        ('where', 'released_year'): {'condition'}, 
        ('condition', '='): {'logical_op'}, 
        ('logical_op', '2021'): {'accept'}, 
        ('logical_op', 'value'): {'accept'},
    }
    #create automaton
    automaton = Automaton(states, inputs, start_state, accept_states, transitions)
    #Sampl query for testing
    query1 = "SELECT track_name, artist FROM playlist WHERE released_month = 12 AND released_year = 2021"
    result1 = accept(automaton, query1)
    print(result1)
    result2 = playlist.query(query1)
    print("Query Results:")
    for song in result2:
        print(song)
    

if __name__ == "__main__":
    main()
