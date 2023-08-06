HLA-Genotyper
=============

HLA-Genotyper is a python software tool to call 4-digit HLA genotypes from RNA-Seq and DNA-Seq directly from BAM files


Installation with easy_install
==============================

The latest version of HLA-Genotyper  is available through `pypi <https://pypi.python.org/pypi>`_. To install, simply type::

    > sudo easy_install hla-genotyper

Or if you do not have sudo privileges, the software can be installed into your user directory with::

    > easy_install --user hla_genotyper

To install easy_install, the following command line will install it into your system Python::

   > sudo curl https://bootstrap.pypa.io/ez_setup.py -o - | python


Installation with pip
=====================

To install pip, type the following command::

   > sudo curl https://bootstrap.pypa.io/get-pip.py|python

Then HLA-Genotyper can be installed with the pip command line::

   > sudo pip install hla-genotyper

or to install in your user directory::

   > pip install --user hla-genotyper


Quick Start 
===========

For certain alignment programs, many reads from the HLA genes are not mapped due to the high level of polymorphisms in the exons. 
For those alignment programs, HLA-Genotyper will need to search among the unmapped reads for HLA read sequences.  For example, bwa aln 
does not align reads well to HLA genes so searching through the unmapped reads is neccesary. The bwa mem program appears better for the MHC region as is the GEMS mapper. 


So for a bam file created with bwa aln, the first step is to create an additional bam file with unmapped reads for hla-genotyper to scan.

The samtools command can be used to create the bam file of unmapped reads::

  > samtools view -u -f 4 mybam.bam > mybam.unmapped.bam 

Once the bam file is available with the unmapped reads, the following commands will complete the HLA genotyping
of the bam files depending on the type of sequencing experiment.


Whole Genome Sequencing::

  > hla-genotyper mybam.bam -u mybam.unmapped.bam -e EUR --genome 

The HLA genotyping results for the whole genome sequencing will be placed in 3 files (hla.EUR.mybam.genome.txt,hla.EUR.mybam.genome.dose,hla.EUR.mybam.genome.log)

Whole Exome Sequencing::

  > hla-genotyper mybam.bam -u mybam.unmapped.bam -e EUR --exome

The HLA genotyping results for the whole exome sequencing will be placed in 3 files (hla.EUR.mybam.rnaseq.txt,hla.EUR.mybam.rnaseq.dose,hla.EUR.mybam.rnaseq.log)

RNA-Seq::

  > hla-genotyper mybam.bam -u mybam.unmapped.bam -e EUR --rnaseq
 
The extra step for scanning unmapped reads is not necessary for the GEMS aligner and possibly the newest version of bwa mem (based on initial testing). In that case,
the creation of the unmapped bam file and the -u option can be dropped::

  >  hla-genotyper mybam.bam -e EUR --rnaseq 

To improve the speed and accuracy of the HLA genotype calls, specifying the ethnicity of the sample is recommended. This option provides a set of  
priors for the various HLA alleles found in the ethnic population.  The ethnicity is specified with with the -e or --ethnicity command line option. 
The available options are 'AFA', 'API', 'EUR', 'HIS' and 'UNK' which correspond to African-American, Asian-Pacific, European, Hispanic and Unknown. 
These ethnic priors for the HLA alleles are based on transplant registry frequencies and supplemented with HLA alleles also found in 1000 genomes. 
For the unknown ethnicity priors,  priors are simply a  uniform distribution for all the HLA alleles found in all 4 populations. However, using the -e UNK option 
will take much longer due to the increase number of HLA allele combinations that are examined along with lower accuracy.


HLA-Genotyper Command line Options
==================================

+------------------+------------------------------------------------------+
|Parameter Option  | Description of HLA-Genotyper Command Line Options    |
+==================+======================================================+
|-h,      --help   | Show this help message                               |
+------------------+------------------------------------------------------+
|-u UNMAPPED_BAM   | Bam file containing unmapped reads.  This file will  |
|                  | be searched for reads with exact matches to known HLA|
|                  | allele sequences. Recommended for alignments by bwa  |
|                  | and most aligners. The samtools command line,        |
|                  | samtools view -u -f 4 mybam.bam > mybam.unmapped.bam |
|                  | will create a bam file of unmapped reads             |
+------------------+------------------------------------------------------+
|-l READLEN	   | This is optional and can be used to specify the read |
|                  | length of the reads in the bam file rather than      |
|                  | letting the program determine this length.  This is  |
|                  | useful when predicting archaic human HLA genotypes   |
|                  | where there is wide range of variable read lengths.  |
+------------------+------------------------------------------------------+
|-m MAPQ	   | Minimum mapping quality                              |
+------------------+------------------------------------------------------+
|--qual BQ	   | Minimum base quality within a read                   |
+------------------+------------------------------------------------------+
|--debug	   | For debugging, list HLA matched read probabilities   |
+------------------+------------------------------------------------------+
|--rnaseq	   | Indicates the bam file is from an RNA-Seq experiment.|
|                  | Reads spanning between exons are included in the     |
|                  | analysis.                                            |
+------------------+------------------------------------------------------+
|--exome	   | Indicates the bam file is from a whole exome or      |
|                  | targeted sequencing experiment.                      |
+------------------+------------------------------------------------------+
|--genome	   | Flag to indicate the input bam file is from a whole  |
|                  | genome experiment.                                   |
+------------------+------------------------------------------------------+
|-s SAMPLE         | To provide the study id in the output file if not    |
|                  | available in the header of the bam file.             |
+------------------+------------------------------------------------------+
|--cn CN           | To provide the Sequencing Center ID for output if not|
|                  | available in the header of the bam file.             |
+------------------+------------------------------------------------------+
|-g GENE           | Limits the analysis to one of the HLA genes          |
|                  | (A,B,C,DRB1, DQB1, DQA1) (Not Recommended)           |
+------------------+------------------------------------------------------+
|-e ETHNICITY	   | To designate the ethnic priors to be used in the     |
|                  | naïve Bayes algorithm.  The prior probabilities for  |
|                  | each ethnic group are stored in the ethnic_priors.txt|
|                  | file. The ethnicity code specified must match one of |
|                  | those in the ethnic_priors.txt file, which are       |
|                  | presently coded EUR, AFA, API, and HIS.              |
+------------------+------------------------------------------------------+
| -r --reference   | To indicate the reference used in the alignment. The |
|                  | options available are 37 or 38 which correspond to   |
|                  | GRCh37/hg19 and GRCH38/hg38.                         |
+------------------+------------------------------------------------------+
| -o               | Directory for output files to be written to.         |
+------------------+------------------------------------------------------+


HLA-Genotyper Output
====================

The HLA-Genotyperscript generates 3 output files: a log file, a dose file and the HLA genotype file. 

    * The log file logs the various steps during the completion of the HLA genotyping.

    * The dose file is a tab-delimited file useful for reading into R scripts for analysis.  
      The file columns correspond to the name of the bam file, id, ethnicity and the list 
      of HLA alleles examined.  The HLA allele columns contained the count of each HLA allele 
      found in the specific population for this individual (0,1,2).  

    * The genotype file lists per line, the Center, bam filename, sample id, ethnic population, 
      the HLA genotype, posterior probability, genotype quality followed by the read counts for
      each allele from mapped and unmapped bam files.


References
==========

HLA-Genotyper Prediction of HLA Genotypes from Next Generation Sequencing Data
J.J. Farrell, G. Jun, L. A. Farrer, A. DeStefano, P. Sebastiani. (Program #1453M)
Presented at the 64th Annual Meeting of The American Society of Human Genetics, October 20, 2014, San Diego, CA.

Contact
=======

For questions and comments contact farrell [ at ] bu.edu
