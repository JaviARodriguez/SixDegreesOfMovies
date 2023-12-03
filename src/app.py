from flask import Flask
from flask import request
from flask import render_template

import requests

from movie import Movie
from graph import Graph
from db import create_connection


app = Flask(__name__)

database = "src/data/movies.db"
connection = create_connection(database)

graph = Graph(connection.cursor())

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/search/<point>")
def search(point):
    query = request.args.get("query")
    
    if query:
        results = search_movies_by_title(query)
    else:
        results = []

    if point == "start":
        post = "/set-movie/start"
        target = "#start-movie"
    else:
        post = "/set-movie/end"
        target = "#end-movie"

    return render_template('search_results.html', results=results, post=post, target=target)

@app.route("/set-movie/<point>", methods=['POST'])
def set_movie(point):
    if request.method == 'POST':
        id = request.form.get("id")
        title = request.form.get("title")
        year = request.form.get("year")
        poster_url = request.form.get("poster_url")

        if point == "start":
            global start_movie
            start_movie = Movie(id, title, year, poster_url)
            movie = start_movie
        else:
            global end_movie
            end_movie = Movie(id, title, year, poster_url)
            movie = end_movie

        return render_template('movie.html', movie=movie)
    
@app.route("/find-path/", methods=['POST'])
def find_path():
    algorithm = request.form.get("algorithm")

    path = []
    if algorithm == "BFS":
        path = graph.BFS()
    elif algorithm == "DFS":
        path = graph.DFS()

    return render_template('path_result.html', path=path)

def search_movies_by_title(title):
    print("hello")

    query = """ SELECT *
                FROM movies
                WHERE title LIKE '%""" + title + "%'" +" ORDER BY title;"

    cursor = connection.cursor()
    cursor.execute(query)

    results = cursor.fetchall()

    movies = []
    for result in results:
        movies.append(Movie(result[0], result[1], result[2], result[3]))

    return movies[:5]

