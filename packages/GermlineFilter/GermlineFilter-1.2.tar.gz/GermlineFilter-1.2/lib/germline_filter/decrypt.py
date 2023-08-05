#!/usr/bin/python

### DECRYPT #######################################################################################
# The script contains functions that decrypt a message, or decrypt an entire file 
# using AES or Blowfish algorithm. If a file is decrypted, the content is and written to a file.
###################################################################################################

from Crypto.Cipher import AES, Blowfish
from Crypto import Random

ENCRYPTION = {'AES': AES, 'Blowfish': Blowfish}


def decrypt_message(ciphertext, keyfile, method):
	'''
	Description:
		Return a string containing the decrypted version of ciphertext.
	Arguments:
		ciphertext, is an encrypted string.
		keyfile, is a path to the file containing the secret key for decryption,
		or the key string itself.
	'''

	iv = ciphertext[: ENCRYPTION[method].block_size]
	if isinstance(keyfile, file):
		with open(keyfile, 'rb') as fo:
			KEY = fo.read()
	else:
		KEY = keyfile
	cipher = ENCRYPTION[method].new(KEY, ENCRYPTION[method].MODE_CBC, iv)
	plaintext = cipher.decrypt(ciphertext[ENCRYPTION[method].block_size :])
	return plaintext.rstrip(b"\0")

