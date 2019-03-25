from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

MIN_ALLOWED_VOICE_DURATION = 0
WRONG_DURATION_ERROR_MESSAGE =  "Sorry, wrong duration"
UNSUPPORTED_MESSAGE_ERROR_MESSAGE = "Your message unsupported, we support voice messages only"
AUDIO_RECEIVED_MESSAGE = "We received your audio, thank you!"
ALLOWED_EMOTIONS = ["angry", "calm", "happy"]
MAIN_MENU_INSTRUCTION_MESSAGE = "Validate or audio send"
VALIDATION_INSTRUCTION_MESSAGE = "Press emotion u think is most likely to be the label for this audio sample"
VOTE_RECEIVED = "We have received your vote!"
MAIN_MENU = ReplyKeyboardMarkup(
                                keyboard=[[KeyboardButton(text="validate"), KeyboardButton(text="vote leaderboard"),
                                KeyboardButton(text="audio leaderboard")]]
                            )
WELCOME_MESSAGE = 'Hello, {}!'
ALL_VALIDATED_MESSAGE = 'all validated, come later'