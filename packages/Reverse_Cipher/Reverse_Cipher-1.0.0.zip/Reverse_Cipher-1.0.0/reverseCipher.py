def reverseCipher(message):
	message = list(message)
	message.reverse()

	return ''.join(message)