Changelog
=========
Kenozooid 0.15.1
----------------
- command line user interface fix after `argparse` library changes

Kenozooid 0.15.0
----------------
- implemented decompression dive planning feature
- added support for OSTC 2C dive computer in ostc driver

Kenozooid 0.14.0
----------------
- command line user interface fixes
- fixed a bug, when R scripts output was unnecessary suppressed

Kenozooid 0.13.0
----------------
- command line user interface fixes
- OSTC parser fixes
- R output should be visible only when command-line verbose option is enabled

Kenozooid 0.12.0
----------------
- support for UDDF 3.2.0

Kenozooid 0.11.0
----------------
- added support for dive enumeration with dive number
- dives can be found using dive number

Kenozooid 0.10.0
----------------
- enable to copy multiple dives
- copy gas mixes information when copying dives
- average depth line on dive details plot is less distracting

Kenozooid 0.9.0
---------------
- added support for dive mode, i.e. open circuit, CCR, etc.
- simplified RMV analysis script to contain only time, average depth and
  average RMV
- fixed average RMV calculation in RMV analysis script

Kenozooid 0.8.0
---------------
- added support for UDDF XML files compressed with bzip2 algorithm
- all commands changing UDDF XML files create backup of the files first

Kenozooid 0.7.0
---------------
- added support for dive average depth
- annotate ascent speeds with "+" and descent speeds with "-" on dive
  profile details plots
- pyserial 2.6 is required, now

Kenozooid 0.6.0
---------------
- support UDDF 3.1
- added support for upgrading UDDF XML files to newer version of UDDF
  specification

Kenozooid 0.5.0
---------------
- maximum descent and ascent rate speeds plotting implemented
- improved gas MOD plotting

Kenozooid 0.4.0
---------------
- setpoint data parsing and plotting implemented
- dive profile annotation with gas and setpoint events improvements
- improved dive info presentation on dive profile plot
- improved quality of dive profile plots in PNG format
- fixed deco ceiling on dive profile details plot to be more accurate

Kenozooid 0.3.0
---------------

- gas data parsing and plotting implemented
- significant speed improvement of UDDF XML data generation while parsing
  dive computer data
- dive adding user interface simplified

Kenozooid 0.2.0
---------------

- data analysis using R scripts described in user manual and supported since
  now
- kenozooid build improvements to distribute kenozooid code and data files
  properly
- plot command changed to accept plot type argument

Kenozooid 0.1.0
---------------

- initial release with support of

  - OSTC dive computer and Sensus Ultra dive data logger (basic data
    import, dive backup, dive simulation)
  - dive profile plotting (profile details and profile comparison)
  - dive calculators (ead, mod, ppO2, ppN2, rmv)
  - basic logbook management support

.. vim: sw=4:et:ai
