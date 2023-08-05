Version 1.2:
=============

New in this version:
--------------------
- This version is hashing CHR:POS, REF and ALT field together. Each line is stored in a set, 
  and the intersection is taken over the set of somatic calls and germline calls.
- The user has the option of choosing the ecryption algorithm - AES of Blowfish
  as well as the hashing method - md5 or sha512
- If not specified, the default values are AES and sha512.
- Removed vcf-query dependency
- Added functionality for extracting the actual germline positions from a somatic vcf.
  This step is done unencrypted, since it's filtering the true germline positions,
  so you should only use it on a local or encrypted server.

Requirements:
	Python Packages:
		- pycrypto

Germline Filter takes as input a preprocessed truth germline VCF file 
(henceforth - "truth") and the VCF outputted by an SNV somatic caller. 

The preprocessing steps for the truth VCF file are:
	- trim to only "CHROM, POS, REF, ALT" fields 
	- hash fields 
	- encrypt the truth file
	- count number of germline calls for a new somatic vcf
	
The output is the number of germline calls in the SNV somatic caller output.

The filtering is done in a safe manner, as the truth VCF will be encrypted 
and hashed. The somatic caller VCF will be hashed, and the hashed values 
are compared. This makes the Germline Filter safe to run on cloud services.


STEPS TO RUN:
1. Preprocess the truth VCF file using "encrypt_truth" command of "germline_filter" 
   Store the 'keyfile' and the 'saltfile' in a safe place.

2. Run the "germline_filter" using the "filter" command.

For further details, please refer to the user manual found at doc/UserManual.pdf

