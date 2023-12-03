from movie import *


class Graph():
    def __init__(self, cursor):
        self.adjacency_list = {}
        self.build_graph(cursor)

    # Builds a graph containing every movie in the database
    def build_graph(self, cursor):
        
        # Select all the movies in the database
        select_all_movies = """ SELECT *
                                FROM Movies; """
        
        cursor.execute(select_all_movies)
        
        # Loop over each movie in the database
        results = cursor.fetchall()
        for result in results:
            from_movie = Movie(result[0], result[1], result[2], result[3])

            # Select all the movies that share an actor with the current movie
            select_all_movies_that_share_actor = f""" SELECT *
                                                      FROM movies
                                                      WHERE movies.id IN
                                                      (
                                                        SELECT movie_id
                                                        FROM actors_in_movie t1
                                                        JOIN (
                                                            SELECT actor_id
                                                            FROM actors_in_movie
                                                            WHERE movie_id = {from_movie.id}
                                                        ) as t2
                                                        ON t1.actor_id = t2.actor_id
                                                        AND t1.movie_id <> {from_movie.id}
                                                      ); """
            
            cursor.execute(select_all_movies_that_share_actor)

            # Insert an edge from the current movie to each movie that shares an actor
            results = cursor.fetchall()
            for result in results:
                to_movie = Movie(result[0], result[1], result[2], result[3])
                self.insert_edge(from_movie, to_movie)

        print(self.adjacency_list)
        print("Graph completed!")


    # Inserts an edge into the adjacency_list from one movie to another
    def insert_edge(self, from_movie, to_movie):
        if from_movie.id not in self.adjacency_list:
            self.adjacency_list[from_movie.id] = []
        
        if to_movie.id not in self.adjacency_list:
            self.adjacency_list[to_movie.id] = []

        self.adjacency_list[from_movie.id].append(to_movie)

    # Finds the shortest path from one movie to another
    # Return a list containing each movie in the path, in order
    def BFS(self):
        return []

    # Finds a path from one movie to another
    # Return a list containing each movie in the path, in order
    def DFS(self):
        return []

