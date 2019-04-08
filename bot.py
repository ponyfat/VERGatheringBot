from mongo_client_wrapper import MongoClientWrapper
import telepot
from telepot.loop import MessageLoop
import time
from telepot.delegate import (per_chat_id_except, per_chat_id_in, create_open, pave_event_space, call)
from constants_and_messages import *
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from format_functions import format_leaderboard
from custom_threads import custom_thread
from directories_manager import create_directory
import sys

TOKEN = '812476155:AAHA1aiwyb6Vy7_RZCSzTfr3vxmSt212RcI'	
MONGO = 'mongodb://localhost:27017/' #default mongo addr
OWNER_ID = 130042164


class GatherValidateChatHandler(telepot.helper.ChatHandler):
	EMOTIONS_KEYBOARD = ReplyKeyboardMarkup(
								keyboard=[[KeyboardButton(text=emotion) for emotion in list(BUTTONS_TO_EMOTIONS.keys())[:3]],
								[KeyboardButton(text=emotion) for emotion in list(BUTTONS_TO_EMOTIONS.keys())[3:7]],
								[KeyboardButton(text=emotion) for emotion in list(BUTTONS_TO_EMOTIONS.keys())[7:]]]
		)

	ALLOWED_COMMANDS = ['/start', '/help'] + list(BUTTONS_TO_EMOTIONS.keys()) + MAIN_MENU_BUTTONS

	def __init__(self, seed_tuple, mongo, **kwargs):
		self._mongo = mongo
		self._mode = "audio_records"
		self._id_for_classification = None
		super(GatherValidateChatHandler, self).__init__(seed_tuple, **kwargs)

	def on_chat_message(self, msg):
		print('msg!', msg)
		content_type, chat_type, chat_id = telepot.glance(msg)
		if content_type == 'voice':
			self._handle_audio_message(msg)
		elif content_type == 'text' and msg['text'] in self.ALLOWED_COMMANDS:
			self._handle_text_command(msg)
		else:
			self.sender.sendMessage(UNSUPPORTED_MESSAGE_ERROR_MESSAGE, reply_markup=MAIN_MENU)
			self.sender.sendMessage(MAIN_MENU_INSTRUCTION_MESSAGE, reply_markup=MAIN_MENU)

	def _handle_audio_message(self, msg):
		print('Duration: ', msg['voice']['duration'])
		if msg['voice']['duration'] >= MIN_ALLOWED_VOICE_DURATION: #right voice
			self._mongo.add_audio_sample(msg)
			self.sender.sendMessage(AUDIO_RECEIVED_MESSAGE, reply_markup=MAIN_MENU)
		else: #too short voice
			self.sender.sendMessage(WRONG_DURATION_ERROR_MESSAGE, reply_markup=MAIN_MENU)

	def _handle_text_command(self, msg):
		if msg['text'] == MAIN_MENU_BUTTONS[0]:
			self._handle_validation(msg)
		elif msg['text'] in BUTTONS_TO_EMOTIONS.keys():
			self._handle_vote(msg)
		elif msg['text'] == '/start':
			self._handle_start(msg)
		elif msg['text'] == '/help':
			self._handle_help(msg)
		elif msg['text'] in MAIN_MENU_BUTTONS[1:-1]:
			self._handle_leaderboard(msg)
		elif msg['text'] == MAIN_MENU_BUTTONS[-1]:
			self._handle_help(msg)


	def _handle_help(self, msg):
		self.sender.sendMessage(HELP_MESSAGE, reply_markup=MAIN_MENU, parse_mode='Markdown')

	def _handle_leaderboard(self, msg):
		if msg['text'] == MAIN_MENU_BUTTONS[1]:
			action = 'vote'
		else:
			action = 'audio'
		leaders, user_info = self._mongo.get_users_entries_leaderboard(msg['from']['username'], action)
		self.sender.sendMessage(format_leaderboard(action, leaders, user_info), reply_markup=MAIN_MENU, parse_mode='Markdown')

	def _handle_validation(self, msg):
		self._id_for_classification = self._mongo.choose_id_for_validation()
		if self._id_for_classification is not None:
			self.sender.sendMessage(VALIDATION_INSTRUCTION_MESSAGE, reply_markup=None)
			self.sender.sendVoice(self._id_for_classification, reply_markup=self.EMOTIONS_KEYBOARD)
		else:
			self.sender.sendMessage(ALL_VALIDATED_MESSAGE, reply_markup=MAIN_MENU)

	def _handle_vote(self, msg):
		self._mongo.add_vote(self._id_for_classification, msg['from']['username'], BUTTONS_TO_EMOTIONS[msg['text']])
		self.sender.sendMessage(VOTE_RECEIVED, reply_markup=MAIN_MENU)

	def _handle_start(self, msg):
		self.sender.sendMessage(WELCOME_MESSAGE.format(msg['from']['username']), reply_markup=MAIN_MENU)

	def on_callback_query(self, msg):
		query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
		print(query_data)

class OwnerHandler(GatherValidateChatHandler):
	def __init__(self, seed_tuple, mongo, **kwargs):
		super(OwnerHandler, self).__init__(seed_tuple, mongo, **kwargs)
		self._announce_mode = False

	def add_get_users_command(original_function):
		def new_function(self, msg):
			content_type, chat_type, chat_id = telepot.glance(msg)
			if content_type == 'text' and msg['text'] == '/get_users':
				self.get_users(msg['text'])
			else:
				original_function(self, msg)
		return new_function

	def add_get_total_stats_command(original_function):
		def new_function(self, msg):
			content_type, chat_type, chat_id = telepot.glance(msg)
			if content_type == 'text' and msg['text'] == '/get_total_stats':
				self.get_total_stats(msg['text'])
			else:
				original_function(self, msg)
		return new_function

	def get_users(self, text):
		usernames = self._mongo.get_all_users()
		self.sender.sendMessage('\n'.join(usernames) + '\nTotal: ' + str(len(usernames)))

	def get_total_stats(self, text):
		total_stats = self._mongo.get_total_stats()
		self.sender.sendMessage('\n'.join(['Total ' + key + ': ' + str(stat) for key, stat in total_stats.items()]))

	@add_get_users_command
	@add_get_total_stats_command
	def on_chat_message(self, msg):
		super(OwnerHandler, self).on_chat_message(msg)


class GatherValidateBot(telepot.DelegatorBot):
	FILES_DIRECTORY = 'raw_audio'

	def __init__(self, token, owner_id):
		# create folder for audio storage
		create_directory(self.FILES_DIRECTORY)

		self._mongo = MongoClientWrapper(MONGO)
		super(GatherValidateBot, self).__init__(token, [
            # Handler for the chat actions
            pave_event_space()(per_chat_id_except([owner_id]), create_open, GatherValidateChatHandler, self._mongo,
            	timeout=1000000),

            pave_event_space()(
                per_chat_id_in([owner_id]), create_open, OwnerHandler, self._mongo, timeout=1000000),
            
            # download voice file
            (self._is_voice, custom_thread(call(self._download_and_store)))
        ])

	def _is_voice(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)

		if content_type != 'voice':
			return None
		else:
			return [] #hashable!

	def _download_and_store(self, seed_tuple):
		self.download_file(seed_tuple[1]['voice']['file_id'], './' + self.FILES_DIRECTORY + '/' +
			seed_tuple[1]['voice']['file_id'] + '.ogg')


bot = GatherValidateBot(TOKEN, OWNER_ID)

MessageLoop(bot).run_as_thread()
print ('BotHosting: I am listening ...')

while 1:
    time.sleep(4)
