'''
Created on 2014-12-04

@author: Cristian Caloian (BoutrosLab - OICR)
'''

from Crypto.Cipher import AES, Blowfish
from Crypto import Random
import csv
import os
from germline_filter.decrypt import decrypt_message
from germline_filter.encrypt import encrypt_message
from germline_filter.preprocess import *
from germline_filter.hash_data import *


### DEFINE CONSTANTS
(CHROM, POS, REF, ALT) = (0, 1, 2, 3)
trim_columns = ['CHROM', 'POS', 'REF', 'ALT'] 


#==================================================================================================
# Encrypt Germline VCF
#==================================================================================================
def encrypt_germline_vcf(args):
	'''
	Description:
		Write the trimmed, hashed and encrypted truth germline vcf to file.
	Arguments:
		args, command line arguments
	'''

	# Make sure output directory exists
	if not os.path.exists(args.outdir):
		os.makedirs(args.outdir)
	
	# Generate encryption key and hashing salt
	key = Random.new().read(32)
	with open(args.outdir + "/" + args.keyfile, 'wb') as fo:
		fo.write(key)
	salt = Random.new().read(32)
	with open(args.outdir + "/" + args.saltfile, 'wb') as fo:
		fo.write(salt)

	for vcf in args.germline:
		trim_content = trim_vcf(vcf)
		outfile = args.outdir + "/" + 'processed_' + args.encryption + "_" + args.hashing + "_" + os.path.basename(vcf) + ".enc"
		with open(outfile, 'wb') as trimmed:
			hashed_content = ''
			for line in trim_content.split('\n'): 
				hashed_line = hash_line(salt, line, args.hashing)
				hashed_content += hashed_line + '\n'
			enc = encrypt_message(hashed_content, key, args.encryption)
			trimmed.write(enc)


#==================================================================================================
# Germline Filter
#==================================================================================================
def filter_vcf(args):
	'''
	Description:
		Print a table of germline calls in each somatic vcf file
		Returns list of counts of germline calls in each somatic vcf file
	Arguments:
		args, command line arguments
	'''
	
	truth_content = decrypt_germline_file(args.germline, args.keyfile, args.encryption)
	germline_data = get_germline_data(truth_content)
	
	germline_call_counts = {}
	print "somatic.vcf\tgermline.count"
	for vcf in args.somatic:
		somatic_data = get_somatic_data(vcf, args.saltfile, args.hashing)
		germline_call_counts[vcf] = len(germline_data.intersection(somatic_data)) 

		print "{somatic}\t{germline}".format(somatic=vcf, germline=germline_call_counts[vcf])

	return germline_call_counts


#==================================================================================================
# Germline Positions
#==================================================================================================
def get_germline_positions(args):
	'''
		Description:
			For each vcf file, write the germline positions found.
		Arguments:
			truth, the truth vcf containing the germline calls.
			vcfs, a list of vcf paths to be filtered for germline calls.
			outdir, string containing the directory path to where the output will be written.
			sample, a string containing the sample name for the truth.
	'''

	if not os.path.exists(os.path.join(args.outdir, args.sample)):
		os.makedirs(os.path.join(args.outdir, args.sample))

	truth_file_trim = trim_vcf(args.truth)
	true_germlines = set(truth_file_trim.split('\n'))

	for vcf in args.vcfs:
		filename = os.path.basename(vcf).strip('.vcf.gz') + '_germline_calls.tsv' 
		outfile = os.path.join(args.outdir, args.sample, filename)		

		with open(outfile, 'w') as fo:
			out = csv.writer(fo, delimiter="\t")
			trim_submission = trim_vcf(vcf)
			vcf_calls = set(trim_submission.split('\n'))
			germline_calls = true_germlines.intersection(vcf_calls)
			header = ['chrom', 'pos']
			out.writerow(header)
			for g in germline_calls:
				row = g.split(':')[0:2]
				out.writerow(row)
