#!/usr/bin/env python

from argparse import ArgumentParser
from logging import debug, info, getLogger
from os import getcwd
from os.path import abspath, basename, isfile, join as path_join
from subprocess import check_output
from shutil import copy, rmtree
from tempfile import mkdtemp

from IPython import embed

def which(program):
    """
    Taken from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def extract_raw_preamble_source(preamble_filename):
    raw_preamble = []
    with open(abspath(preamble_filename), 'r') as file_containing_preamble:
        for line in file_containing_preamble:
            # assume that everything up to the \begin{document} comprises the preamble
            if line.find("begin{document}") >= 0:
                break
            elif line.find("documentclass") == -1:
                line = line.strip()
                if len(line) > 0:
                    raw_preamble.append(line)
    
    return raw_preamble


def filter_raw_preamble(raw_preamble):
    acceptable_line_prefaces = ['\usepackage', r'\new', r'\def', '\usetikzlibrary', '\usepgfplotslibrary']
    filtered_preamble = []
    for line in raw_preamble:
        if line[0] != "%" and any([True for preface in acceptable_line_prefaces if line.find(preface) != -1]):
            filtered_preamble.append(line)
    return filtered_preamble


def main(input_tikz, height, width, output, keep_pdf, eng, preamble=None, verbose=False):
    if verbose is True:
        logger = getLogger()
        logger.setLevel(10)

    debug('Checking if input tikz file exists')
    if isfile(abspath(input_tikz)) is not True:
        raise StandardError('input tikz file does not exist')
    
    debug("Looking for typesetting engine")
    if which(eng) is None:
        raise StandardError('selected typesetting engine (%s) is not installed on this system' % typeset_eng)
    
    debug('Attempting to find high quality pdf to eps converter, pdftops')
    if which('pdftops') is None:
        info('For better quality, it is recommended that you install pdftops, using epspdf instead')
        if which('epspdf') is None:
            raise StandardError('pdf to eps converter (epspdf) is not installed on this system')
        else:
            ps_converter = "epspdf"
    else:
        ps_converter = "pdftops"
        
    temporary_directory = mkdtemp()
    debug("Outputting to the following temporary directory: %s" % temporary_directory)
        
    output_filename_base = basename(input_tikz).split('.')
    output_filename_base.pop()
    output_filename_base = '.'.join(output_filename_base)
    
    output_preamble = [r"\documentclass[]{standalone}"]

    if preamble is not None and isfile(abspath(preamble)):
        preamble = extract_raw_preamble_source(preamble)
        output_preamble.extend(filter_raw_preamble(preamble))

    if len(output_preamble) == 1:
        output_preamble.append("\usepackage{tikz,pgfplots}")
        

    document = []
    document.append(r"\begin{document}")
    if height is not None and width is not None:
        document.append(r"\setlength\figureheight{%spt}" % height)
        document.append(r"\setlength\figurewidth{%spt}" % width)

    tikz_source_file = open(input_tikz, 'r')
    for line in tikz_source_file:
        document.append(line.rstrip())
    tikz_source_file.close()
        
    document.append(r"\end{document}")

    tex_filename = path_join(temporary_directory, "%s.tex" % output_filename_base)

    tex_file = open(tex_filename, 'w')

    tex_file.write('\n'.join(output_preamble + document))
    tex_file.close()
    
    typeset_command = [eng]
    if eng == "xelatex" or eng == "pdflatex":
        typeset_command.append("-output-directory=%s" % temporary_directory)
    elif eng == "lualatex":
        typeset_command.append("--output-directory=%s" % temporary_directory)

    typeset_command.append(tex_filename)
    
    debug("Attempting to run the following typesetting command: %s" % (' '.join(typeset_command)))
    typesest_result = check_output(typeset_command)

    pdf_filename = path_join(temporary_directory, "%s.pdf" % output_filename_base)

    eps_filename = path_join(temporary_directory, "%s.eps" % output_filename_base)

    ps_conversion_command = [ps_converter]
    if ps_converter == "pdftops":
        ps_conversion_command.append("-eps")
    ps_conversion_command.append(pdf_filename)
    ps_conversion_command.append(eps_filename)

    debug("Attempting to run the following eps conversion command: %s" % (' '.join(ps_conversion_command)))
    ps_conversion = check_output(ps_conversion_command)
    
    output_dir = abspath(output)
    copy(eps_filename, output_dir)

    if keep_pdf is True:
        copy(pdf_filename, output_dir)

    rmtree(temporary_directory)


if __name__ == "__main__":
    parser = ArgumentParser(description='This is a simple script for converting a figure from tikz source to eps.  An external .tex source file (likely the manuscript for which the figure was created) can be optionally included to extract the premable and the packages and definitions included therein.  A pdf version of the figure can also be optionally exported.')

    parser.add_argument('input_tikz',
                        metavar='input_tikz',
                        type=str,
                        help='the tikz figure to be converted')
                        
    parser.add_argument('--height',
                        metavar='h',
                        type=str,
                        help='the height of the output figure in pt',
                        default=None)

    parser.add_argument('--width',
                        metavar='w',
                        type=str,
                        help='the width of the output figure in pt',
                        default=None)                   
                        
    parser.add_argument('--preamble',
                        metavar='FILE',
                        type=str,
                        help='a file from which to extract the latex preamble',
                        default=None)
                        
    parser.add_argument('--output',
                        metavar='DIRECTORY',
                        type=str,
                        help='the directory in which to store the outputted figure(s)',
                        default=getcwd())
                        
    parser.add_argument('--eng',
                        metavar='ENGINE',
                        type=str,
                        help='the typesetting engine used to generate the figure (xelatex is the default)',
                        default='xelatex')

    parser.add_argument('--keep_pdf',
                        help='outputs a pdf version of the figure',
                        default=False,
                        action='store_true')

    parser.add_argument('--verbose',
                        help='prints detailed log information',
                        default=False,
                        action='store_true')
    
    args = parser.parse_args()
    main(**vars(args))