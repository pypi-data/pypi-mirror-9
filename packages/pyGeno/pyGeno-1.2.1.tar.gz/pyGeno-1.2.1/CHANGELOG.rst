1.2.1
=====

* Fixed tests

1.2.0
=====
* BUG FIX: get()/iterGet() now works for SNPs and Indels

* BUG FIX: Default SNP filter used to return unwanted Nones for insertions

* BUG FIX: Added cast of lines to str in VCF and CasavaSNP parsers. Sometimes unicode caracters made the translation bug  

* BUG FIX: Corrected a typo that caused find in Transcript to recursively die 

* Added a new AgnosticSNP type of SNPs that can be easily made from the results of any snp caller. To make for the loss of support for casava by illumina. See SNP.AgnosticSNP for documentation

* pyGeno now comes with the murine reference genome GRCm38.78

* pyGeno now comes with the human reference genome GRCh38.78, GRCh37.75 is still shipped with pyGeno but might be in the upcoming versions

* pyGeno now comes with a datawrap for common dbSNPs human SNPs (SNP_dbSNP142_human_common_all.tar.gz)

* Added a dummy AgnosticSNP datawrap example for boostraping

* Changed the interface of the bootstrap module

* CSV Parser has now the ability to stream directly to a file


1.1.7
=====

* BUG FIX: looping through CSV lines now works

* Added tests for CSV

1.1.6
=====

* BUG FIX: find in BinarySequence could not find some subsequences at the tail of sequence

1.1.5
=====

* BUG FIX in default SNP filter

* Updated description

1.1.4
=====

* Another BUG FIX in progress bar

1.1.3
=====

* Small BUG FIX in the progress bar that caused epochs to be misrepresented

* 'Specie' has been changed to 'species' everywhere. That breaks the database the only way to fix it is to redo all importations

1.1.2
=====

* Genome import is now much more memory efficient

* BUG FIX: find in BinarySequence could not find subsequences at the tail of sequence

* Added a built-in datawrap with only chr1 and y

* Readme update with more infos about importation and link to doc
 
1.1.1
=====

Much better SNP filtering interface
------------------------------------
Easier and much morr coherent:

* SNP filtering has now its own module

* SNP Filters are now objects

* SNP Filters must return SequenceSNP, SNPInsert, SNPDeletion or None objects

1.0.0
=====
Freshly hatched

