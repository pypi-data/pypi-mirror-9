#!/usr/bin/python

### HASH_DATA ######################################################################################
# This script is used for hashing fields of a vcf file
####################################################################################################

from Crypto.Hash import MD5, SHA512
from random import shuffle
import re

### DEFINE CONSTANTS ###############################################################################
(CHROM, POS, REF, ALT) = (0, 1, 2, 3)
HASHING = {'md5': MD5, 'sha512': SHA512}


### FUNCTIONS ######################################################################################
def hash_line(salt, line, method):
	'''
	Description:
		Return a string containg the hashed value of the fields in line.
		CHROM and POS are separated by ":" in order to avoid hashed values
		conflicts.
	Arguments:
		line, a tab-separated string with fields: CHROM, POS, REF, ALT
		method, is a string containing the hashing method to be used.
	'''
	hashed_line = HASHING[method].new(salt + line).hexdigest() 
	return hashed_line

