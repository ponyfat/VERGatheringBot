# Gather Validate Bot for Voice Emotion Recognition dataset gathering

Telegram bot for collecting and validating the data for Voice Emotion Recognition in Russian.

## Mongo

MongoDB is used for the storage. Variable MONGO in bot.py should contain the needed url.

## How is the data collected and processed
Each person with the bot can either add a new audiofile into the database or help to label the existing audiofiles.

If the person commits a new audio into the bot, the information about it is stored in the db. Audio file is downloaded in saved in ./raw_audio.

All the audios than go into the voting pool. Each audio needs to collect 5 labeling votes to be validated and stored in the dataset. The labels are: angry/happy/sad/calm (this can be adjusted). In labeling mode respondents with the bot get the random audio from the voting pool and mark it as one of the labels or as trash. If the audio collects 5 labels it is marked with the most common and stored in the ./csv_dataset/dataset.csv.
