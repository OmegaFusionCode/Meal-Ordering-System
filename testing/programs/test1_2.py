from database import Database 

db = Database("localhost", "pi", "raspberry", "cafeteria")

while True:
    query = raw_input()
    params = (raw_input(),)
    if params[0] != "":
        print(db.executeQuery(query, params))
    else:
        print(db.executeQuery(query))
