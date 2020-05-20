from db.config import Config, Database

config = Config()

db = Database(config)

connection = db.connection()

db.init_db()

db.close()
