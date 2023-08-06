from flask import Blueprint, abort
from flask.ext.restful import Resource, Api, reqparse
import dataset
import config

db = dataset.connect(config.DATABASE_URI)
db['habits'].create_index(['slug'])
db['entries'].create_index(['date'])

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

def get_habits():
    return [i['slug'] for i in list(db['habits'].all())]

class HabitList(Resource):
    def get(self):
        return list(db['habits'].all())

class HabitNames(Resource):
    def get(self):
        return {i['slug']: i['name'] for i in list(db['habits'].all())}

class Habit(Resource):
    def get(self, slug):
        return db['habits'].find_one(slug=slug)

    def post(self, slug):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        habit_id = db['habits'].insert(dict(name=args['name'], slug=slug))
        return db['habits'].find_one(id=habit_id)

class Entry(Resource):
    def get(self, date):
        entry = db['entries'].find_one(date=date)

        habits = get_habits()
        for habit in habits:
            if habit not in entry:
                entry[habit] = False

        for k, v in entry.iteritems():
            if v is None:
                entry[k] = False

        return entry

    def post(self, date):
        parser = reqparse.RequestParser()
        parser.add_argument('habit', type=str, action='append')
        args = parser.parse_args()

        entry = dict()
        entry['date'] = date
        habits = get_habits()
        if ('habit' in args):
            input_habits = args['habit']
        if not input_habits:
            input_habits = []
        for habit in input_habits:
            if habit not in habits:
                abort(400)
        for habit in habits:
            entry[habit] = (habit in input_habits)

        db['entries'].upsert(entry, ['date'])
        return db['entries'].find_one(date=date)

class HabitToggle(Resource):
    def post(self, date, habit):
        entry = db['entries'].find_one(date=date)
        if habit not in entry:
            abort(400)
        entry[habit] = not entry[habit]
        db['entries'].upsert(entry, ['date'])
        return db['entries'].find_one(date=date)

class EntryExport(Resource):
    def get(self):
        return list(db['entries'].all())

api.add_resource(HabitList, '/habits')
api.add_resource(HabitNames, '/habits/names')
api.add_resource(Habit, '/habits/<string:slug>')
api.add_resource(EntryExport, '/entries/export')
api.add_resource(Entry, '/entries/<string:date>')
api.add_resource(HabitToggle, '/entries/<string:date>/<string:habit>')