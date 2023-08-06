LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters = LETTERS.lower()

def decrypt(cipher, key):
	message = []
	for symbol in cipher:
		if symbol in LETTERS:
			index = (LETTERS.find(symbol) - key) % len(LETTERS)
			message.append(LETTERS[index])
		elif symbol in letters:
			index = (letters.find(symbol) - key) % len(letters)
			message.append(letters[index])
		else:
			message.append(symbol)
	return ''.join(message)

def bruteForce(cipher):
	for key in range(len(letters)):
		message = decrypt(cipher, key)
		print 'Key#%s: %s' % (key, message)