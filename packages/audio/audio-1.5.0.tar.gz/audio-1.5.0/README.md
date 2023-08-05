
Audio
================================================================================

The `audio` package exists to simplify the installation of the following packages:

  - `audio.bitstream`,
  - `audio.coders`,
  - `audio.filters`,
  - `audio.fourier`,
  - `audio.frames`,
  - `audio.index`,
  - `audio.io`,
  - `audio.lp`,
  - `audio.quantizers`,
  - `audio.shrink`, 
  - `audio.wave`.

The easy way to install it is to use the [pip] package manager:
  
    $ sudo pip install --upgrade audio

Use the same command to update all packages to their latest stable release. 

Follow the instructions below if `pip` is not available on your system.

-----

Most of the dependencies of these packages are automatically managed, but
some dependencies still need to be manually installed beforehand:

  1. **The `pip` package installer.** 
     [Installation instructions](https://pip.pypa.io/en/latest/installing.html)
     for all platforms.

     On Ubuntu:

         $ sudo apt-get install python-pip

     [pip]: https://pip.pypa.io/en/latest/index.html

  2. **[NumPy] -- Numerical Python.** 
     Unless you know what you are doing, use existing binary packages.

     On Ubuntu:

         $ sudo apt-get install python-numpy

     [Numpy]: http://www.numpy.org/

  3. **[PyAudio] -- Python bindings for PortAudio.**
     Refer to [PyAudio] for general installation instructions.

     On Ubuntu:

         $ sudo apt-get install python-pyaudio

     [PyAudio]: http://people.csail.mit.edu/hubert/pyaudio/

  4. **[NLTK] and [TIMIT] -- Natural Language Toolkit & Acoustic-Phonetic Speech Corpus**

     Detailled NLTK installation instructions are available [here][NLTK-install]. 
     TIMIT is an extra corpus that be installed separately, see [here][NLTK-install-data].

     On Ubuntu, install NLTK with:

         $ sudo apt-get install python-nltk

     and then the TIMIT corpus with:

         $ python -c "import nltk; nltk.download('timit')"

     [NLTK]: http://www.nltk.org/
     [TIMIT]: https://catalog.ldc.upenn.edu/LDC93S1
     [NLTK-install]: http://www.nltk.org/install.html
     [NLTK-install-data]: http://www.nltk.org/data.html

