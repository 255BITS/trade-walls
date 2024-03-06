from peewee import *

# Step 1: Establish a connection to the database
db = SqliteDatabase('trading.sqlite')

# Step 2: Define the models
class BaseModel(Model):
    class Meta:
        database = db

class Wall(BaseModel):
    bid_price = CharField()
    keep = CharField(default="0")
    ask_price = CharField()
    quantity = CharField()
    pair = CharField()

class OrderExecution(BaseModel):
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    amount = CharField()
    unit = CharField()
    pair = CharField()
    executed_at = DateField(null=True)
    wall = ForeignKeyField(Wall, backref='executions')

# Step 3: Create the tables
db.connect()
db.create_tables([Wall, OrderExecution])
