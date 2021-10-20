from database import Database 

db = Database("localhost", "pi", "raspberry", "cafeteria")

while True:
    query = raw_input()
    print(db.executeQuery(query))
