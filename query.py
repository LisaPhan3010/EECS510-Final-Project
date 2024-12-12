from datetime import datetime
import re
import csv

# Song class to represent individual songs
class Song:
    def __init__(self, track_name, artist, released_year, released_month, released_day, streams, bpm, key, mode):
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
        return f"{self.track_name} by {self.artist} ({self.released_date.date()}) - Streams: {self.streams}, BPM: {self.bpm}, Key: {self.key}, Mode: {self.mode}"

class Playlist:
    def __init__(self):
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)
    
    def query(self, sql_query):
    # Parse the SQL-like query
        match = re.match(r"SELECT (.+) FROM playlist WHERE (.+)", sql_query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid query format")
        selected_attributes = match.group(1).split(',')
        selected_attributes = [attr.strip() for attr in selected_attributes]
        conditions_str = match.group(2)
        conditions = self.parse_conditions(conditions_str)
        result = []
        for song in self.songs: 
            if self.match_song(song, conditions):
                result.append({attr: getattr(song, attr) for attr in selected_attributes})
        return result


    def parse_conditions(self, conditions_str):
        conditions = {}
        condition_parts = re.split(r" AND | OR ", conditions_str, flags=re.IGNORECASE)

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

            # Convert numeric values to integers
            if value.isdigit():
                value = int(value)

            conditions[key] = (operator, value)

        return conditions

    def match_song(self, song, conditions):
        for key, (operator, value) in conditions.items():
            song_value = getattr(song, key, None)

            # Handle invalid key
            if song_value is None:
                return False

            # Perform the comparison
            if not self.compare(song_value, value, operator):
                return False

        return True

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

def main():
    playlist = Playlist()

    # Load songs from a CSV file
    try:
        with open("spotify-2023.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
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

    # Query 1: Find songs released in 2023
    query = "SELECT track_name, artist FROM playlist WHERE released_day = 17 AND released_year = 2023"
    result1 = playlist.query(query)
    print("Query Results:")
    for song in result1:
        print(song)


if __name__ == "__main__":
    main()