import mvmv
import sqlite3
import sys

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

mvmv.movemovie(sys.argv[1], "./", cursor)
