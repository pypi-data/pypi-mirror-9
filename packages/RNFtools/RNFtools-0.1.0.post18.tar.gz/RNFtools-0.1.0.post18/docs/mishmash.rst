Simulation of NGS reads
======================

.. contents::
   :depth: 3


MIShmash
--------

MIShmash is a part of RNFtools responsible for simulation of Next-Generation Sequencing reads. It employs
existing read simulators and combines the obtained reads into bigger single set.


Usage
^^^^^

Create there an empty file named ``Snakefile``, which will serve as a configuration script.
Then save the following content into it:

.. code-block:: python
	
	# required line, it should be the first line of all your configuration scripts
	import rnftools

	# this line tells MIShmash that there will be a new sample
	rnftools.mishmash.sample("new_sample")
	
	# then you can add arbitrary number of sources
	rnftools.mishmash.ArtIllumina(
		fa="my_fast.fa",
		number_of_reads=10000,
		read_length_1=100,
		read_length_2=0,
	)
	
	# if you want to create more simulated samples, call again the mishmash.sample
	# function but with another sample name


	# these lines are mandatory as the last lines of the file
	include: rnftools.mishmash.include()
	rule: input: rnftools.mishmash.input()


Supported simulators
^^^^^^^^^^^^^^^^^^^^

ART
~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Weichun Huang                                                           |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://www.niehs.nih.gov/research/resources/software/biostatistics/art/ |
+--------------+-------------------------------------------------------------------------+
| Publication: | Huang, W. *et al.*                                                      |
|              | ART: a next-generation sequencing read simulator.                       |
|              | *Bioinformatics* **28**\(4), pp. 593--594, 2011.                        |
+--------------+-------------------------------------------------------------------------+


ART Illumina
""""""""""""

.. autoclass:: rnftools.mishmash.ArtIllumina
        :members:
        :inherited-members:
        :show-inheritance:


CuReSim
~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Ségolène Caboche                                                        |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://www.pegase-biosciences.com/tools/curesim/                        |
+--------------+-------------------------------------------------------------------------+
| Publication: | Caboche, S. *et al.*                                                    |
|              | Comparison of mapping algorithms used in high-throughput sequencing:    |
|              | application to Ion Torrent data.                                        |
|              | *BMC Genomics* **15**\:264, 2014.                                       |
+--------------+-------------------------------------------------------------------------+

.. autoclass:: rnftools.mishmash.CuReSim
        :members:
        :inherited-members:
        :show-inheritance:


DwgSim
~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Niels Homer                                                             |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://github.com/nh13/dwgsim                                           |
+--------------+-------------------------------------------------------------------------+

**Format of read names (before conversion to RNF)**

.. code-block::

	(.*)_([0-9]+)_([0-9]+)_([01])_([01])_([01])_([01])_([0-9]+):([0-9]+):([0-9]+)_([0-9]+):([0-9]+):([0-9]+)_(([0-9abcdef])+)


1)  contig name (chromsome name)
2)  start end 1 (one-based)
3)  start end 2 (one-based)
4)  strand end 1 (0 - forward, 1 - reverse)
5)  strand end 2 (0 - forward, 1 - reverse)
6)  random read end 1 (0 - from the mutated reference, 1 - random)
7)  random read end 2 (0 - from the mutated reference, 1 - random)
8)  number of sequencing errors end 1 (color errors for colorspace)
9)  number of SNPs end 1
10) number of indels end 1
11) number of sequencing errors end 2 (color errors for colorspace)
12) number of SNPs end 2
13) number of indels end 2
14) read number (unique within a given contig/chromosome)


.. autoclass:: rnftools.mishmash.DwgSim
        :members:
        :inherited-members:
        :show-inheritance:
 
WgSim
~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Heng Li                                                                 |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://github.com/lh3/wgsim                                             |
+--------------+-------------------------------------------------------------------------+

.. autoclass:: rnftools.mishmash.WgSim
        :members:
        :inherited-members:
        :show-inheritance:


Supported simulators
^^^^^^^^^^^^^^^^^^^^

For completeness, we mention also other simulators of NGS reads.

pIRS
~~~~

+--------------+-------------------------------------------------------------------------+
| Authors:     | Jianying Yuan, Eric Biggers                                             |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://code.google.com/p/pirs                                           |
|              | http://github.com/galaxy001/pirs                                        |
+--------------+-------------------------------------------------------------------------+
| Publication: | Hu, X., *et al.*                                                        |
|              | pIRS: Profile-based Illumina pair-end reads simulator.                  |
|              | *Bioinformatics* **28**\(11):1533--1535, 2012.                          |
+--------------+-------------------------------------------------------------------------+

Mason
~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Manuel Holtgrewe                                                        |
+--------------+-------------------------------------------------------------------------+
| URL:         | https://www.seqan.de/projects/mason/                                    |
+--------------+-------------------------------------------------------------------------+
| Publication: | Holtgrewe, M.                                                           |
|              | Mason -- a read simulator for second generation sequencing data.        |
|              | Technical Report TR-B-10-06,                                            |
|              | Institut für Mathematik und Informatik, Freie Universität Berlin, 2010. |
+--------------+-------------------------------------------------------------------------+

SimNGS
~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Tim Massingham                                                          |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://www.ebi.ac.uk/goldman-srv/simNGS/                                |
+--------------+-------------------------------------------------------------------------+

GemSIM
~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Kerensa E. McElroy                                                      |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://sourceforge.net/projects/gemsim                                  |
+--------------+-------------------------------------------------------------------------+
| Publication: | McElroy, K. E. *et al.*                                                 |
|              | GemSIM: general, error-model based simulator of next-generation         |
|              | sequencing data.                                                        |
|              | *BMC Genomics* **13**\:74, 2012.                                        |
+--------------+-------------------------------------------------------------------------+

FlowSIM
~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Susanne Balzer                                                          |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://biohaskell.org/Applications/FlowSim                              |
+--------------+-------------------------------------------------------------------------+
| Publication: | Balzer, S. *et al.*                                                     |
|              | Characteristics of 454 pyrosequencing data -- enabling realistic        |
|              | simulation with flowsim.                                                |
|              | *Bioinformatics* **26**\(18):i420--i425, 2010.                          |
+--------------+-------------------------------------------------------------------------+

SimSEQ
~~~~~~

+--------------+-------------------------------------------------------------------------+
| Authors:     | John St. John                                                           |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://github.com/jstjohn/SimSeq                                        |
+--------------+-------------------------------------------------------------------------+


PbSIM
~~~~~

+--------------+-------------------------------------------------------------------------+
| Authors:     | Michiaki Hamada, Yukiteru Ono                                           |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://code.google.com/p/pbsim                                          |
+--------------+-------------------------------------------------------------------------+
| Publication: | Ono, Y. *et al.*                                                        |
|              | PBSIM: PacBio reads simulator -- toward accurate genome assembly.       |
|              | *Bioinformatics* **29**\(1):119--121, 2013.                             |
+--------------+-------------------------------------------------------------------------+


SInC
~~~~

+--------------+-------------------------------------------------------------------------+
| URL:         | http://sincsimulator.sourceforge.net                                    |
+--------------+-------------------------------------------------------------------------+
| Publication: | Pattnaik, S. *et al.*                                                   |
|              | SInC: an accurate and fast error-model based simulator for SNPs, Indels |
|              | and CNVs coupled with a read generator for short-read sequence data.    |
|              | *BMC Bioinformatics* **15**\:40, 2014.                                  |
+--------------+-------------------------------------------------------------------------+


Wessim
~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Sangwoo Kim                                                             |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://sak042.github.io/Wessim/                                         |
+--------------+-------------------------------------------------------------------------+


FASTQSim
~~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Anna Shcherbina                                                         |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://sourceforge.net/projects/fastqsim                                |
+--------------+-------------------------------------------------------------------------+
| Publication: | Shcherbina, A.                                                          |
|              | FASTQSim: platform-independent data characterization and in silico      |
|              | read generation for NGS datasets.                                       |
|              | *BMC Research Notes* **7**\:533, 2014.                                  |
+--------------+-------------------------------------------------------------------------+


XS
~~

+--------------+-------------------------------------------------------------------------+
| Authors:     | Diogo Pratas, Armando J. Pinho, João M. O. S. Rodrigues                 |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://bioinformatics.ua.pt/software/xs                                 |
+--------------+-------------------------------------------------------------------------+
| Publication: | Pratas, D. *et al.*                                                     |
|              | XS: a FASTQ read simulator.                                             |
|              | *BMC Research Notes* **7**\:40, 2014.                                   |
+--------------+-------------------------------------------------------------------------+


Sherman
~~~~~~~

+--------------+-------------------------------------------------------------------------+
| Author:      | Felix Krueger                                                           |
+--------------+-------------------------------------------------------------------------+
| URL:         | http://www.bioinformatics.babraham.ac.uk/projects/sherman               |
+--------------+-------------------------------------------------------------------------+
