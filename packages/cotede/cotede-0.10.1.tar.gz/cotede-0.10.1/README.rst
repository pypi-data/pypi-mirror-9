=============
CoTe De l'eau
=============

This package is intended to quality control CTD stations by applying
a sequence of tests. It uses the Seabird package to interpret the
SeaBird's .cnv output file.

This is the result from several generations of quality control systems,
which started in 2006, while I was in charge of the quality control
of termosalinographs at AOML-NOAA, USA. Later I was advising the
quality control of the brazilian hydrography of PIRATA.

CoTeDe can apply different quality control procedures:
  - The default GTSPP or EGOOS procedure;
  - A custom set of tests and user defined thresholds;
  - A novel approach based on Anomaly Detection, described by `Castelao 2015 <http://arxiv.org/abs/1503.02714>`_;

Quick howto
___________

First load the CTD data

|    pqc = cotede.qc.fProfileQC('example.cnv')

The keys() will give you the data loaded from the CTD, simillar to the output from the seabird.fCNV

|    pqc.keys()

To see one of the read variables listed on the previous step

|    pqc['temperature']

The flags are stored at pqc.flags and is a dictionary, being one item per variable evaluated. For example, to see the flags for the secondary salinity instrument, just do

|    pqc.flags['salinity2']

or for a specific test

|    pqc.flags['salinity2']['gradient']

To evaluate a full set of profiles at once, use the class ProfileQCCollection, like:

|    dataset = ProfileQCCollection('/path/to/data/', inputpattern=".*\.cnv")
|    dataset.flags['temperature'].keys()

The class cotede.qc.ProfileQCed is equivalent to the cotede.qc.ProfileQC, but it already mask the non approved data (flag != 1). Another it can also be used like:

|    from seabird import cnv
|    data = cnv.fCNV('example.cnv')
|
|    import cotede.qc
|    ped = cotede.qc.ProfileQCed(data)

Support and Documentation
-------------------------

http://cotede.readthedocs.org/en/latest/

How I see quality control
-------------------------

Quality control is different then data processing. On the processed data, the quality control/quality assurance means to check what looks fine. It is very important that the data is properly sampled and processed. The quality control procedures can't go back on time and fix improper sampling, but only tell you that the data don't looks fine.

Why CoTeDe?
-----------

For a long time I had the idea of the anomaly detection technique in mind, but I only really formalize the procedure in 2013, when I spent few months in Toulouse. 
The full name of this package is CoTe De l'eau, which I understand as something near to "rating the water". 
The short name is cotede, to make easier for the users to remember, since it is the quality control of COnductivity TEmperature and DEpth (cotede). 
The french name is a kind of tribute to the great time that I spent in France with Bia and the croissants that were converted in code lines.

