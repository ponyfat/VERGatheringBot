from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

MIN_ALLOWED_VOICE_DURATION = 0
WRONG_DURATION_ERROR_MESSAGE =  "Слишком короткое сообщение"
UNSUPPORTED_MESSAGE_ERROR_MESSAGE = "Поддерживаются только голосовые сообщения!"
AUDIO_RECEIVED_MESSAGE = "Мы получили ваше сообщение. Спасибо!"
ALLOWED_EMOTIONS = ["angry", "calm", "excited", "sad", "spam"]
BUTTONS_TO_EMOTIONS = {"Злость" : "angry", 
					   "Cпокойствие": "calm",
					   "Cчастье": "excited",
					   "Грусть" : "sad",
					   "Cпам": "spam"}
MAIN_MENU_INSTRUCTION_MESSAGE = "Определи эмоцию или отправь головое сообщение"
VALIDATION_INSTRUCTION_MESSAGE = "Выбери эмоцию, которая на твой взгяд точнее всего описывает это сообщение"
VOTE_RECEIVED = "Ваш голос принят!"
MAIN_MENU = ReplyKeyboardMarkup(
                                keyboard=[[KeyboardButton(text="Проверить сообщение"), KeyboardButton(text="Таблица лидеров по количеству проверенных сообщений"),
                                KeyboardButton(text="Таблица лидеров по количеству отправленных сообщений")]]
                            )
MAIN_MENU_BUTTONS = ["Проверить сообщение", "Таблица лидеров по количеству проверенных сообщений", "Таблица лидеров по количеству отправленных сообщений"]
WELCOME_MESSAGE = 'Привет, {}! Спасибо, что подключился к моему небольшому исследованию. Его тема: определение эмоций человека по голосу. Для его реализации мне необходимо собрать датасет из голосовых сообщений и соответстующих им эмоций, в чем я и прошу тебя мне помочь. Для этого отправь сюда любое голосовое сообщение, либо выбери эмоцию к загруженным. Спасибо!'
ALL_VALIDATED_MESSAGE = 'Проверять больше нечего. Приходи позже'