from peewee import *

# Step 1: Establish a connection to the database
db = SqliteDatabase('trading.sqlite')

# Step 2: Define the models
class BaseModel(Model):
    class Meta:
        database = db

class Wall(BaseModel):
    TYPE_CHOICES = (('buy', 'buy'), ('sell', 'sell'))

    type = CharField(choices=TYPE_CHOICES)
    price = CharField()
    pair = CharField()
    min_holdings = CharField()
    quantity = CharField()

class OrderExecution(BaseModel):
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    amount = CharField()
    unit = CharField()
    pair = CharField()
    wall = ForeignKeyField(Wall, backref='executions')

# Step 3: Create the tables
db.connect()
db.create_tables([Wall, OrderExecution])
