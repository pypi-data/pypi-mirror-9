.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

This package contains the access API and descriptions for the `2012 NIST Speaker Recognition Evaluation`_.
It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the database should be downloaded from the original URL.


Speaker Recognition Protocol on the NIST SRE 2012 Database
----------------------------------------------------------

The `2012 NIST Speaker Recognition Evaluation`_ (SRE12) is part of an ongoing series that starts in 1996.

In this package, we implement speaker recognition protocols (both Male and Female) for the NIST SRE 2012.
The file lists of the development set were designed by the I4U consortium during its participation to the competition.
Special thanks to Rahim Saeidi (original link of the lists: http://cls.ru.nl/~saeidi/file_library/I4U.tgz).
The file names were then normalized following the `PRISM definition`_.

This package is automatically downloaded/used by :py:mod:`spear.nist_sre12` to reproduce the results of Idiap Research Institute at SRE12.
:py:mod:`spear.nist_sre12` itself relies on :py:mod:`spear`, an open-source speaker recognition toolbox developed at Idiap_.
The list files can also be used independently as explained below.

If you use this package and/or its results, please cite the following publications:

1. The Spear paper published at ICASSP 2014:

  .. code-block:: latex

    @inproceedings{spear,
      author = {Khoury, E. and El Shafey, L. and Marcel, S.},
      title = {Spear: An open source toolbox for speaker recognition based on {B}ob},
      booktitle = {IEEE Intl. Conf. on Acoustics, Speech and Signal Processing (ICASSP)},
      year = {2014},
      url = {http://publications.idiap.ch/downloads/papers/2014/Khoury_ICASSP_2014.pdf},
    }


2. The paper that described the development set used by the I4U consortium:

  .. code-block:: latex

    @inproceedings{Saedi_INTERSPEECH_2013,
       author = {Saeidi, Rahim and others},
       month = {aug},
       title = {I4U Submission to NIST SRE 2012: a large-scale collaborative effort for noise-robust speaker verification},
       booktitle = {INTERSPEECH},
       year = {2013},
       location = {Lyon, France},
       pdf = {http://publications.idiap.ch/downloads/papers/2013/Saedi_INTERSPEECH_2013.pdf}
    }


3. Bob as the core framework used to run the experiments:

  .. code-block:: latex

    @inproceedings{Anjos_ACMMM_2012,
      author = {Anjos, Andr\'e and El Shafey, Laurent and Wallace, Roy and G\"unther, Manuel and McCool, Christopher and Marcel, S\'ebastien},
      title = {Bob: a free signal processing and machine learning toolbox for researchers},
      year = {2012},
      month = {oct},
      booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
      publisher = {ACM Press},
      url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
    }

Getting the data
~~~~~~~~~~~~~~~~

You need to order the NIST SRE databases (Fisher, Switchboard, and Mixer): http://www.ldc.upenn.edu/Catalog/CatalogEntry.jsp?catalogId=LDC2013S03

Please follow the instructions and the evaluation plan given by NIST: http://www.nist.gov/itl/iad/mig/sre12.cfm

Depending on the release year, the data may need to be flatten and reorganized.
Please, follow the file structure as appearing when running:

.. code-block:: sh

  $ bin/bob_dbmanage.py nist_sre12 dumplist

For this purpose, you will need the utilities provided by NIST with the database, as well as `sox`_.


Decompressing the data and splitting the audio channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The data provided by NIST are compressed in a non-standard format.
NIST supplies a binary called `w_decode` to perform the decompression.
Therefore, you should decompress all the files using the following command (where NIST_FOLDER/bin is the one containing the `w_decode` utility:

.. code-block:: sh

  $ NIST_FOLDER/bin/w_decode -o pcm $compressedfile $decompressedfile

Several files are in stereo and hence contain two audio channels.
These files needs to be split using a script similar to the following one:

.. code-block:: sh

  $ decompressedfileStereo=`basename $decompressedfile .sph`
  $ num=`soxi $decompressedfile | grep Channels | cut -c 18`
  $ echo $num
  $ if [ $num -eq 2 ]
  $ then # File is stereo
  $   echo sox $decompressedfile -c 1 $outputDir/${decompressedfileStereo}-a.sph mixer -l
  $   sox $decompressedfile -c 1 $outputDir/${decompressedfileStereo}-a.sph mixer -l
  $   sox $decompressedfile -c 1 $outputDir/${decompressedfileStereo}-b.sph mixer -r
  $ else # File is mono
  $   echo cp $decompressedfile $outputDir/
  $   cp $decompressedfile $outputDir/
  $ fi


Adding noise
~~~~~~~~~~~~

In order to better represent the SRE12 evaluation set, 2 noisy versions (SNR=6dB and SNR=15dB) of the same segments were included to the development set (both target models and test utterances).
This can be done using `FaNT <http://dnt.kr.hsnr.de/download.html>`_

The noise samples were mainly collected from freesound.org and include HVAC and crowd noise.
They are available on request.
The description of the added noise for each of the audio files can be found here under ``bob/db/nist_sre12/noise_description``.


Speech enhancement
~~~~~~~~~~~~~~~~~~

The denoising of the audio signal can be done using `QIO <http://www1.icsi.berkeley.edu/Speech/papers/qio>`_.


Using independently the file lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file lists of the development and evaluation sets are shipped with this package.
They can be used independently, and can be found under ``bob/db/nist_sre12/prism``.
The file lists of the development set were prepared by the I4U consortium.



The Database Interface
----------------------

The :py:class:`bob.db.nist_sre12.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing both interfaces :py:class:`bob.db.verification.utils.SQLiteDatabase` and :py:class:`bob.db.verification.utils.ZTDatabase`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.nist_sre12.Database`.


.. _idiap: http://www.idiap.ch
.. _bob: https://www.idiap.ch/software/bob
.. _nist_sre12: http://www.nist_sre12.org/
.. _spear: https://github.com/bioidiap/bob.spear
.. _spear.nist_sre12: https://github.com/bioidiap/spear.nist_sre12
.. _2012 NIST Speaker Recognition Evaluation: http://www.nist.gov/itl/iad/mig/sre12.cfm
.. _PRISM definition: http://code.google.com/p/prism-set
.. _sox: http://sox.sourceforge.net/


