MiModD - Identify Mutations from Whole-Genome Sequencing Data
*************************************************************

MiModD is an integrated solution for efficient and user-friendly analysis of 
whole-genome sequencing (WGS) data from laboratory model organisms. 
It enables geneticists to identify the genetic mutations present in an organism 
starting from just raw WGS read data and a reference genome without the help of 
a trained bioinformatician.

MiModD is designed for good performance on standard hardware and enables WGS 
data analysis for most model organisms on regular desktop PCs.

MiModD can be installed under Linux and Mac OS with minimal software 
requirements and a simple setup procedure. As a standalone package it can be 
used from the command line, but can also be integrated seamlessly and easily 
into any local installation of a Galaxy bioinformatics server providing a 
graphical user interface, database management of results and simple composition 
of analysis steps into workflows.

Hardware and software requirements
==================================

Hardware
--------

MiModD performs very well on standard desktop PCs provided that they meet the 
memory requirements imposed by the genome size of the organism that is analyzed. 

8 GB RAM are required (16 GB recommended) to analyze WGS data from typical 
invertebrate model organisms like Drosophila and C. elegans and between 16 and 
32 GB RAM are necessary for working with small vertebrate genomes like that 
of several fish species (e.g., Medaka, pufferfish, zebrafish). 

Of note, these memory requirements concern only the initial mapping step of WGS 
analysis. Variant calling, annotation and filtering steps starting from 
*aligned* reads files can all be carried out with MiModD with minimal memory 
requirements.

See our compilation of hardware requirements at 
http://mimodd.readthedocs.org/en/latest/hardware.html for more details on this 
topic and additional hardware recommendations.

Software
--------

MiModD runs under LINUX and Mac OS and requires Python 3.2 or higher.

Installation of SnpEff (http://snpeff.sourceforge.net) for variant annotation, 
which in turn requires Java, is optional.

If you would like to set up your own `local Galaxy server 
<https://wiki.galaxyproject.org/Admin/GetGalaxy>`_, to enjoy a graphical user 
interface and the possibility to turn your machine into an in-house server for 
WGS analysis, you will need Python 2.6 or 2.7 installed alongside Python 3. 
You will also need Mercurial to clone the current Galaxy source code as the 
basis of the installation.

Obtaining and installing MiModD
===============================
Installation instructions (covering also the installation of all required 
and optional software) can be found in the INSTALL file included in this 
distribution.

Documentation and help
======================
We have prepared a detailed `online documentation 
<http://mimodd.readthedocs.org/en/latest/>`_ of the package including a tutorial for 
beginners. If you experience problems with any part of MiModD or you think you 
found a bug in the software, the preferred way of letting us and others know is 
through posting to the MiModD user group at 
https://groups.google.com/forum/#!forum/mimodd or via email to 
mimodd@googlegroups.com.


