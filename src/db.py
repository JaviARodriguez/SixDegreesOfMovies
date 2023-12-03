import requests

import sqlite3
from sqlite3 import Error


def initialize_db():
    database = "src/data/movies.db"

    create_movies_table_sql = """ CREATE TABLE IF NOT EXISTS movies (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        release_year integer,
                                        poster_path text
                                    ); """
    
    create_actors_table_sql = """ CREATE TABLE IF NOT EXISTS actors (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL
                                    ); """
    
    create_actors_in_movie_table_sql = """ CREATE TABLE IF NOT EXISTS actors_in_movie (
                                                actor_id integer,
                                                movie_id integer,
                                                PRIMARY KEY (actor_id, movie_id)
                                            ); """

    connection = create_connection(database)

    if connection is not None:
        create_table(connection, create_movies_table_sql)
        create_table(connection, create_actors_table_sql)
        create_table(connection, create_actors_in_movie_table_sql)
    else:
        print("Error! Could not create connection to the database!")

    insert_movies_from_tmdb(connection)
    insert_actors_from_tmdb(connection)

    connection.close()


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file, check_same_thread=False)
        return connection
    except Error as e:
        print(e)

    return connection


def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)


def insert_movies_from_tmdb(connection):
    query = "discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_date.gte=1920-01-01&sort_by=popularity.desc&with_original_language=en"
    response = request_from_tmdb(query)

    total_pages = 0

    if response is not None:
       total_pages = response.json()["total_pages"]

    page = 0

    num_of_movies = 0
    while page < total_pages and num_of_movies < 10000:
        query = f"discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&primary_release_date.gte=1920-01-01&sort_by=popularity.desc&with_original_language=en"
        response = request_from_tmdb(query)

        results = []
        if response is not None:
            results = response.json()["results"]

        for result in results:
            movie = {
                "id": result["id"],
                "title": result["title"],
                "release_year": result["release_date"][:4],
                "poster_path": "https://image.tmdb.org/t/p/original" + f"{result['poster_path']}"
            }

            insert_movie(connection, movie)
            num_of_movies += 1
        
        page += 1


def insert_movie(connection, movie):
    sql = ''' INSERT OR IGNORE INTO movies(id,title,release_year,poster_path)
              VALUES(:id,:title,:release_year,:poster_path) '''
    
    cursor = connection.cursor()
    cursor.execute(sql, movie)
    connection.commit()

    return cursor.lastrowid

def insert_actors_from_tmdb(connection):
    sql = """ SELECT id
              FROM movies; """
    
    cursor = connection.cursor();
    cursor.execute(sql)

    movie_ids = cursor.fetchall()
    for row in movie_ids:
        movie_id = row[0]
        query = f"movie/{movie_id}/credits?language=en-US"
        response = request_from_tmdb(query)

        results = []
        if response is not None:
            results = response.json()["cast"]

        for result in results:
            if result["known_for_department"] == "Acting":
                actor = {
                    "id": result["id"],
                    "name": result["name"]
                }
                insert_actor(connection, actor, movie_id)


def insert_actor(connection, actor, movie_id):
    actors_sql = ''' INSERT OR IGNORE INTO actors(id,name)
                     VALUES(:id,:name) '''
    
    actors_in_movie_sql = ''' INSERT OR IGNORE INTO actors_in_movie(actor_id,movie_id)
                             VALUES(?,?) '''
    
    cursor = connection.cursor()
    cursor.execute(actors_sql, actor)
    cursor.execute(actors_in_movie_sql, [actor["id"], movie_id])
    connection.commit()

    return cursor.lastrowid


def request_from_tmdb(query):
    url = "https://api.themoviedb.org/3/" + query

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOWIwNGQ2ZjIxYTU0MTkxMTM3MmJhODM4M2RhNTliMiIsInN1YiI6IjY1Njc2MzI1ZDk1NDIwMDBhYjY1ODAyMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.qsqFo7oc1joR6UqKAO4GBun9nxrLKa0_kGea2-J37Hw"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code >= 400:
        return None
    
    return response


if __name__ == '__main__':
    initialize_db()

