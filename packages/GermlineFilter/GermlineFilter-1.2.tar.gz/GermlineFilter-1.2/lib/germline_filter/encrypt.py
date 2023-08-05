#!/usr/bin/python

### ENCRYPT #######################################################################################
# The script contains functions that encrypt a message, or encrypt an entire file 
# using the AES algorithm. If a file is encrypted, the content is (gzipped) and
# written to a file.
###################################################################################################

from Crypto.Cipher import AES, Blowfish
from Crypto import Random

ENCRYPTION = {'AES': AES, 'Blowfish': Blowfish}

def pad(s, method):
	'''
	Description:
		Pad the string with zeros, such that it is a multiple of the block_size (16 bytes)
	Arguments:
		s, is a string to be padded.
		method, is a string containing the encryption method.
	'''
	return s + b"\0" * (ENCRYPTION[method].block_size - len(s) % ENCRYPTION[method].block_size)


def encrypt_message(message, key, method):
	'''
	Description:
		Encrypt the message using AES encryption method.
	Arguments:
		message, is a string to be encrypted.
		key, is string of length 32 bytes, used to encrypt the message.
		method, is a string containing the encryption method.
	'''
	message = pad(message, method)
	iv = Random.new().read(ENCRYPTION[method].block_size)
	cipher = ENCRYPTION[method].new(key, ENCRYPTION[method].MODE_CBC, iv)
	return iv + cipher.encrypt(message)

