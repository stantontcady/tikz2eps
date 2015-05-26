tikz2eps
========

A simple script for converting a tikz figure into an encapsulated postscript (eps).  Essentially, tikz2eps is a wrapper around a few built in commands which simplifies the creation of eps (and pdf) figures from tikz.

##Requirements##
tikz2eps is written completely in Python and was tested using version 2.7.6; it should be compatible with most versions of Python 2. It relies on the builtin libraries listed below.
```python
argparse, logging, os, subprocess, shutil, tempfile
```

Additionally, it uses the XeLaTeX typesetting engine by default, but can be used with other engines if specified by the user (more detail provided below). Finally, for converting from pdf to eps, `pdftops` is used, with `epspdf` as a fallback.  The former is available [here](http://www.foolabs.com/xpdf/download.html).

##Usage##
tikz2eps takes several arguments, but only the path to the input tikz source is required. The following simple example will take a source tikz file and convert it to an eps which will be placed in the current working directory (likely the directory from which the script is being executed).

```python
./tikz2eps.py ~/my_figure.tikz
```

I generally use the .tikz extension for source files, however the extension should not matter.  The following is a list of the optional parameters. 

* `--height` - Controls the height of the figure in units of pt (see note in incomplete features).
* `--width` - Controls the width of the figure in units of pt (see note in incomplete features).
* `--preamble` - The LaTeX source from which the preamble should be extracted; this is generally the file into which the figure was originally typeset. If the source figure imports all the needed packages and defines all variables this step is unnecessary.
* `--output` - The directory into which the output figure should be saved (default is current working directory).
* `--eng` - The typesetting engine to be used (default is XeLaTeX).
* `--keep_pdf` - Boolean to specify whether or not a pdf version of the figure should be kept (default is False).
* `--verbose` - Changes log level to 10 so as to print debugging messages.

##Known Gotchas##
If a preamble source is included, tikz2eps will step through the part of the file between `\documentclass` and `\begin{document}` and extract most of the lines therein. Rather than try to maintain a blacklist of lines that will cause typesetting the standalone file to fail, the approach taken is to only permit certain lines (listed below). If your figure is not rendering correctly or if the conversion hangs, one of the preamble lines may have been excluded.

Allowed preamble lines:

* `\include{\*}`
* `\new\*`
* `\def\*`
* `\usetikzlibrary`
* `\usepgfplotslibrary`


##Incomplete Features##
At present, the figure height and width only work to control the size of figures that are set with the `\figureheight` and `\figurewidth` LaTeX variables; this is a common approach when generating figures using [matlab2tikz](https://github.com/nschloe/matlab2tikz) or [matplotlib2tikz](https://github.com/nschloe/matplotlib2tikz).