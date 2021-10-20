# Created by third-parties
import pymysql
from pymysql.cursors import DictCursor

class Database():
    
    def __init__(self, hostname, user, password, dbname):
        """Database constructor method"""
        self.hostname = hostname
        self.user = user
        self.password = password
        self.dbname = dbname
        self.conn = None
        self.cursor = None

    def openConn(self):
        """Opens connection to the database"""
        if self.conn is None:
            self.conn = pymysql.connect(self.hostname, self.user, self.password, self.dbname, cursorclass=DictCursor, autocommit=True)
            self.cursor = self.conn.cursor()    # Creates a cursor object, which we can interface the database with

    def closeConn(self):
        """Closes connection to the database"""
        if self.conn is not None:
            self.conn.close()
            self.conn = None    # Makes sure that the conn property is set to None in case we want to use the openConn method
        
    def executeQuery(self, query, params=None, close=True):
        self.openConn()     # Opens the database connection
        self.cursor.execute(query, params)      # Executes the query as a parameterised SQL query
        data = self.cursor.fetchall()      # This returns a list containing each record in the form of a dictionary
        if close:
            self.closeConn()    # Closes the database connection
        if len(data) > 0:
            return data     # Returns the data that we needed
        else:
            return []
