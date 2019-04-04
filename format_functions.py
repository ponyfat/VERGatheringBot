# -*- coding: utf-8 -*-

def format_leaderboard(action, leaders, user_info):
	field = action + '_cnt'
	arglist = [action]
	for leader in leaders:
		arglist = arglist + [leader['username'], str(leader[field])]
	for i in range(len(arglist), 7):
		arglist.append('...')
	arglist = arglist + [str(user_info[field]), str(user_info['place'])]
	arglist = wordlist_to_markdown(arglist[1:])
	if arglist[0] == 'audio':
		return audio_leaders(arglist)
	else:
		return vote_leasers(arglist)

def wordlist_to_markdown(arglist):
	new_arglist = []
	for arg in arglist:
		new_arglist.append(arg_to_markdown(arg))
	return new_arglist

def word_to_markdown(arg):
	return arg.replace("_", "\_")

def audio_leaders(arglist):
	return """*Больше всеx сообщений отправили:*

	🥇 1. %s : %s
	🥈 2. %s : %s
	🥉 3. %s : %s

	______________________
	*Вы:*
	Отправлено сообщений: %s
	Место: %s 🎉""" % tuple(arglist)

def vote_leasers(arglist):
	return """*Больше всеx голосовали:*

	🥇 1. %s : %s
	🥈 2. %s : %s
	🥉 3. %s : %s

	______________________
	*Вы:*
	Отдано голосов: %s
	Место: %s 🎉""" % tuple(arglist)
