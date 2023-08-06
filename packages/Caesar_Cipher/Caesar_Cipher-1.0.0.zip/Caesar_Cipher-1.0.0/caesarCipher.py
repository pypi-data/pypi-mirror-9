LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters = LETTERS.lower()

def encrypt(message, key):

	cipher = []

	for letter in message:

		if letter.upper() in LETTERS:
			if letter.isupper():
				index = (LETTERS.find(letter) + key) % len(LETTERS)
				cipher.append(LETTERS[index])
			else:
				index = (letters.find(letter) + key) % len(letters)
				cipher.append(letters[index])
		else:
			cipher.append(letter)

	return ''.join(cipher)

def decrypt(cipher, key):

	plain = []

	for letter in cipher:
		if letter.upper() in LETTERS:
			if letter.isupper():
				index = (LETTERS.find(letter) - key) % len(LETTERS)
				plain.append(LETTERS[index])
			else:
				index = (letters.find(letter) - key) % len(letters)
				plain.append(letters[index])
		else:
			plain.append(letter)

	return ''.join(plain)