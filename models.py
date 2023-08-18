# models.py

from flask_mongoengine import MongoEngine

db = MongoEngine()

class Medicine(db.Document):
    name = db.StringField(required=True)
    photo = db.StringField()
    before_breakfast = db.BooleanField(default=False)
    after_breakfast = db.BooleanField(default=False)
    breakfast = db.BooleanField(default=False)
    before_lunch = db.BooleanField(default=False)
    after_lunch = db.BooleanField(default=False)
    lunch = db.BooleanField(default=False)
    before_dinner = db.BooleanField(default=False)
    after_dinner = db.BooleanField(default=False)
    dinner = db.BooleanField(default=False)
    notes = db.StringField()

    def __repr__(self):
        return f'<Medicine {self.name}>'
