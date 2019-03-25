def format_leaderboard(action, leaders, user_info):
	field = action + '_cnt'
	arglist = [action]
	for leader in leaders:
		arglist = arglist + [leader['username'], str(leader[field])]
	for i in range(len(arglist), 7):
		arglist.append('...')
	arglist = arglist + [str(user_info[field]), str(user_info['place'])]
	print(arglist, len(arglist))
	return """Leaders of %s:
	1. %s %s
	2. %s %s
	3. %s %s
	////////////////////////////
	You: 
	scored: %s
	place: %s""" % tuple(arglist)
