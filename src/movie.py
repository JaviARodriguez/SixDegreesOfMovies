import requests


class Actor:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Movie:
    def __init__(self, id, title, year, poster_url):
        self.id = int(id)
        self.title = title
        self.year = year
        self.poster_url = poster_url

    def __str__(self):
        return f"{self.title} ({self.year})"