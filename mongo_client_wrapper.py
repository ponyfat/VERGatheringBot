from pymongo import MongoClient
from random import choice
import pymongo
from csv_writer_wrapper import CSVWriterWrapper

# !!! ADD CONSTANT EMOTIONS LINK

class MongoClientWrapper(object):
	MAX_VOTES = 5
	CSV_FIELDS = ['first_name', 'last_name', 'username', 'language_code', 'duration', 'file_id', 'vote_calm', 'vote_angry', 'vote_excited',
	'vote_sad', 'vote_spam', 'vote_total']

	def __init__(self, mongo_uri):
		print('MongoClientWrapper: mongo client wrapper initializing...')

		self._client = MongoClient(mongo_uri)
		self._db = self._client.voice_samples_database
		self._voice_samples_collection = self._db.voice_samples_collection
		self._entries_collection = self._db.entries_collection

		# when there are enough votes for the sample we store it in csv dataset file
		self._csv_writer_wrapper = CSVWriterWrapper(self.CSV_FIELDS)

	def _ids_for_validation(self):
		print('MongoClientWrapper: id list initializing...')
		return [x['file_id'] for x in 
		list(self._voice_samples_collection.find({ 'vote_total': { '$lt': self.MAX_VOTES } }, {'file_id': 1}))]

		for post in self._voice_samples_collection.find({ 'vote_total': { '$lt': self.MAX_VOTES } })['file_id']:
			self._ids_for_validation.append(post['file_id'])

	
	def add_audio_sample(self, msg):
		print('MongoClientWrapper: audio sample adding to db...')

		self._voice_samples_collection.insert_one({'first_name': msg['from']['first_name'], 'last_name': msg['from']['last_name'],
			'username': msg['from']['username'], 'language_code': msg['from']['language_code'],
			'duration': msg['voice']['duration'], 'file_id': msg['voice']['file_id'],
			'vote_calm': 0, 'vote_angry': 0, 'vote_excited': 0, 'vote_sad': 0, 'vote_spam': 0, 'vote_total': 0})

		self._entries_collection_cnt_increment(msg['from']['username'], 'audio')

	
		
	def add_vote(self, file_id, username, emotion):
		print('MongoClientWrapper: adding vote...')

		voted_emotion = 'vote_' + emotion
		self._voice_samples_collection.update_one({'file_id': file_id},
			{'$inc': {'vote_total': 1, voted_emotion : 1}})
		if self._voice_samples_collection.find_one({'file_id': file_id})['vote_total'] == 5:
			row_dict = dict(self._voice_samples_collection.find_one({'file_id': file_id}))
			row_dict.pop('_id')
			self._csv_writer_wrapper.write_line(row_dict)
		self._entries_collection_cnt_increment(username, 'vote')


	def _entries_collection_cnt_increment(self, username, action):
		incremented_field = action + '_cnt'
		if self._entries_collection.find_one({'username': username}):
			self._entries_collection.update_one({'username': username}, {'$inc': {incremented_field: 1}})
		elif action == 'vote':
			self._entries_collection.insert_one({'username': username, 'audio_cnt': 0, 'vote_cnt': 1})
		elif action == 'audio':
			self._entries_collection.insert_one({'username': username, 'audio_cnt': 1, 'vote_cnt': 0})


	def choose_id_for_validation(self):
		ids_for_validation = self._ids_for_validation()
		if not ids_for_validation:
			return None
		else:
			return choice(ids_for_validation)

	def get_users_entries_leaderboard(self, username, action):
		field = action + '_cnt'
		leaders = list(self._entries_collection.find().sort(field, pymongo.DESCENDING).limit(3))

		if not self._entries_collection.find_one({'username': username}):
			self._entries_collection.insert_one({'username': username, 'audio_cnt': 0, 'vote_cnt': 0})
		user_score = self._entries_collection.find_one({'username': username})[field]

		user_place = self._entries_collection.find({field : {'$gte': user_score}}).count()
		return leaders, {field: user_score, 'place': user_place}

