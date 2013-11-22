import os
from tornado import ioloop,web
from tornado.escape import json_encode
from pymongo import MongoClient
import json
from bson import json_util
from bson.objectid import ObjectId


MONGODB_DB_URL = os.environ.get('OPENSHIFT_MONGODB_DB_URL') if os.environ.get('OPENSHIFT_MONGODB_DB_URL') else 'mongodb://localhost:27017/'
MONGODB_DB_NAME = os.environ.get('OPENSHIFT_APP_NAME') if os.environ.get('OPENSHIFT_APP_NAME') else 'getbookmarks'

client = MongoClient(MONGODB_DB_URL)
db = client[MONGODB_DB_NAME]

class IndexHandler(web.RequestHandler):
	def get(self):
		self.render("index.html")

class StoriesHandler(web.RequestHandler):
	def get(self):
		stories = db.stories.find()
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps(list(stories),default=json_util.default))
		

	def post(self):
		story_data = json.loads(self.request.body)
		story_id = db.stories.insert(story_data)
		print('story created with id ' + str(story_id))
		self.set_header("Content-Type", "application/json")
		self.set_status(201)
		

class StoryHandler(web.RequestHandler):
	def get(self , story_id):
		story = db.stories.find_one({"_id":ObjectId(str(story_id))})
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps((story),default=json_util.default))


settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug" : True
}

application = web.Application([
	(r'/', IndexHandler),
	(r'/index', IndexHandler),
	(r'/api/v1/stories',StoriesHandler),
	(r'/api/v1/stories/(.*)', StoryHandler)
],**settings)

if __name__ == "__main__":
	application.listen(8888)
	ioloop.IOLoop.instance().start()
