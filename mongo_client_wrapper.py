from pymongo import MongoClient
from random import choice
import pymongo
from csv_writer_wrapper import CSVWriterWrapper

# !!! ADD CONSTANT EMOTIONS LINK

class MongoClientWrapper(object):
	MAX_VOTES = 5
	CSV_FIELDS = ['first_name', 'last_name', 'username', 'language_code', 'duration', 'file_id',
	'vote_calm', 'vote_angry', 'vote_excited', 'vote_surprised', 'vote_disgust', 'vote_fear',
	'vote_sad', 'vote_spam', 'vote_idk', 'vote_total']

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

	def add_user(self, msg):
		user_id = msg['from']['id']
		username = self._get_username_from_msg(msg)
		full_name = self._get_fullname_from_msg(msg)

		if not username:
			username = full_name

		if not self._entries_collection.find_one({'user_id': user_id}):
			self._entries_collection.insert_one({'user_id': user_id, 'username': username, 'audio_cnt': 0, 'vote_cnt': 0})

	
	def add_audio_sample(self, msg):
		print('MongoClientWrapper: audio sample adding to db...')

		self._voice_samples_collection.insert_one({
			'first_name': msg['from'].get('first_name', 'None'),
			'last_name': msg['from'].get('last_name', 'None'),
			'username': msg['from'].get('username', 'None'),
			'language_code': msg['from'].get('language_code', 'None'),
			'duration': msg['voice'].get('duration', 'None'),
			'file_id': msg['voice']['file_id'],
			'vote_calm': 0,
			'vote_angry': 0,
			'vote_excited': 0,
			'vote_surprised': 0,
			'vote_disgust': 0,
			'vote_fear': 0,
			'vote_sad': 0,
			'vote_spam': 0,
			'vote_idk': 0,
			'vote_total': 0})

		self._entries_collection_cnt_increment(msg['from']['id'], 'audio',
			self._get_username_from_msg(msg), self._get_fullname_from_msg(msg))

	
	def add_vote(self, file_id, emotion, msg):
		print('MongoClientWrapper: adding vote...')

		voted_emotion = 'vote_' + emotion

		self._voice_samples_collection.update_one({'file_id': file_id},
			{'$inc': {'vote_total': 1, voted_emotion : 1}})
		print(self._voice_samples_collection.find_one({'file_id': file_id})['vote_total'])
		if self._voice_samples_collection.find_one({'file_id': file_id})['vote_total'] == 5:
			print('before writin!')
			row_dict = dict(self._voice_samples_collection.find_one({'file_id': file_id}))
			row_dict.pop('_id')
			self._csv_writer_wrapper.write_line(row_dict)
		self._entries_collection_cnt_increment(msg['from']['id'], 'vote',
			self._get_username_from_msg(msg), self._get_fullname_from_msg(msg))

	def _get_username_from_msg(self, msg):
		return msg['from'].get('username', None)

	def _get_fullname_from_msg(self, msg):
		return msg['from'].get('first_name', '') + msg['from'].get('last_name', '')

	def _entries_collection_cnt_increment(self, user_id, action, username, full_name):
		if username:
			self._update_entries_for_user_id_index(user_id, username)
		else:
			username = full_name

		incremented_field = action + '_cnt'
		if self._entries_collection.find_one({'user_id': user_id}):
			self._entries_collection.update_one({'user_id': user_id}, {'$inc': {incremented_field: 1}})
		elif action == 'vote':
			self._entries_collection.insert_one({'user_id': user_id, 'username': username, 'audio_cnt': 0, 'vote_cnt': 1})
		elif action == 'audio':
			self._entries_collection.insert_one({'user_id': user_id, 'username': username, 'audio_cnt': 1, 'vote_cnt': 0})


	def choose_id_for_validation(self):
		ids_for_validation = self._ids_for_validation()
		if not ids_for_validation:
			return None
		else:
			return choice(ids_for_validation)

	def get_users_entries_leaderboard(self, action, msg):
		user_id = msg['from']['id']
		username = self._get_username_from_msg(msg)
		full_name = self._get_fullname_from_msg(msg)

		field = action + '_cnt'
		leaders = list(self._entries_collection.find({}, {'user_id': 0}).sort(field, pymongo.DESCENDING).limit(3))

		if username:
			self._update_entries_for_user_id_index(user_id, username)
		else:
			username = full_name

		if not self._entries_collection.find_one({'user_id': user_id}):
			self._entries_collection.insert_one({'user_id': user_id, 'username': username, 'audio_cnt': 0, 'vote_cnt': 0})

		user_score = self._entries_collection.find_one({'user_id': user_id})[field]

		user_place = self._entries_collection.find({field : {'$gte': user_score}}).count()
		return leaders, {field: user_score, 'place': user_place}

	def _update_entries_for_user_id_index(self, user_id, username):
		if self._entries_collection.find_one({'username': username}) and 'user_id' not in dict(self._entries_collection.find_one({'username': username})).keys():
			self._entries_collection.update_one({'username': username}, {'$set' :{'user_id': user_id}})

	def get_all_users(self):
		return self._entries_collection.distinct('username')

	def get_total_stats(self):
		total_stats = {}
		total_stats['audio'] = self._voice_samples_collection.count()
		total_stats['users'] = self._entries_collection.count()
		total_stats['validated audio'] = self._voice_samples_collection.find({'vote_total' : 5}).count()
		return total_stats

	def get_all_user_ids(self):
		print(list(self._entries_collection.find({})))
		return self._entries_collection.distinct('user_id')
