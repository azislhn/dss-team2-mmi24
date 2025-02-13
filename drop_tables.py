from database import Database

db = Database()
db.drop_tables()

db._create_tables()