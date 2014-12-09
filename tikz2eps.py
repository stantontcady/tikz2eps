#!/usr/bin/env python

from argparse import ArgumentParser
from os import listdir, getcwd, remove, rename
from os.path import abspath, basename, isfile, join as path_join
from subprocess import check_output
from time import time


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


def main(input_tikz, height, width, output_dir, keep_pdf, typeset_eng, preamble_src=None):
    input_tikz = abspath(input_tikz)
    if isfile(abspath(input_tikz)) is not True:
        raise StandardError('input tikz file does not exist')
    
    if which(typeset_eng) is None:
        raise StandardError('selected typesetting engine (%s) is not installed on this system' % typset_eng)
    
    if which('pdftops') is None:
        print 'For better quality, it is recommended that you install pdftops, using epspdf'
        if which('epspdf') is None:
            raise StandardError('pdf to eps converter (epspdf) is not installed on this system')
        else:
            ps_converter = "epspdf"
    else:
        ps_converter = "pdftops"
        
    output_filename_base = basename(input_tikz).split('.')
    output_filename_base.pop()
    output_filename_base = '.'.join(output_filename_base)

    if preamble_src is not None and isfile(abspath(preamble_src)):
        file_containing_preamble = open(abspath(preamble_src), 'r')

        preamble = [r"\documentclass[]{standalone}"]
        for line in file_containing_preamble:
            # assume that everything up to the \begin{document} comprises the preamble
            if line.find("begin{document}") >= 0:
                break
            elif line.find("documentclass") == -1:
                line = line.strip()
                # if line.find("%") != 0:
                preamble.append(line)

        file_containing_preamble.close()
        
    temporary_filename_base = "tmp_%i" % time()

    document = []
    document.append(r"\begin{document}")
    document.append(r"\setlength\figureheight{%sem}" % height)
    document.append(r"\setlength\figurewidth{%sem}" % width)
    document.append(r"\input{%s}" % abspath(input_tikz))
    document.append(r"\end{document}")
    
    output_dir = abspath(output_dir)
    
    tex_filename = path_join(output_dir, "%s.tex" % temporary_filename_base)

    tex_file = open(tex_filename, 'w')
    tex_file.write('\n'.join(preamble + document))
    tex_file.close()
    
    typeset_command = [typeset_eng]
    if typeset_eng == "xelatex":
        typeset_command.append("-output-directory=%s" % output_dir)

    typeset_command.append(tex_filename)

    typesest_result = check_output(typeset_command)

    pdf_filename = path_join(output_dir, "%s.pdf" % temporary_filename_base)

    eps_filename = path_join(output_dir, "%s.eps" % output_filename_base)

    ps_conversion_command = [ps_converter]
    if ps_converter == "pdftops":
        ps_conversion_command.append("-eps")
    ps_conversion_command.append(pdf_filename)
    ps_conversion_command.append(eps_filename)

    ps_conversion = check_output(ps_conversion_command)

    if keep_pdf is True:
        rename(pdf_filename, path_join(output_dir, "%s.pdf" % output_filename_base))

    temp_filelist = [f for f in listdir(output_dir) if f.startswith(temporary_filename_base)]
    for temp_file in temp_filelist:
        remove(path_join(output_dir, temp_file))


if __name__ == "__main__":
    parser = ArgumentParser(description='This is a simple script for converting a figure from tikz source to eps.  An external .tex source file (likely the manuscript for which the figure was created) can be optionally included to extract the premable and the packages and definitions included therein.  A pdf version of the figure can also be optionally exported.')

    parser.add_argument('input_tikz',
                        metavar='input_tikz',
                        type=str,
                        help='the tikz figure to be converted')
                        
    parser.add_argument('--height',
                        metavar='h',
                        type=str,
                        help='the height of the output figure in em')

    parser.add_argument('--width',
                        metavar='w',
                        type=str,
                        help='the width of the output figure in em')                   
                        
    parser.add_argument('--preamble_src',
                        metavar='src',
                        type=str,
                        help='a file from which to extract the latex preamble',
                        default=None)
                        
    parser.add_argument('--output_dir',
                        metavar='dir',
                        type=str,
                        help='the directory in which to store the outputted figure(s)',
                        default=getcwd())

    parser.add_argument('--keep_pdf',
                        help='outputs a pdf version of the figure',
                        default=False,
                        action='store_true')
                        
    parser.add_argument('--typeset_eng',
                        metavar='eng',
                        type=str,
                        help='the typsetting engine used to generate the figure (xelatex is the default)',
                        default='xelatex')
    
    args = parser.parse_args()
    main(**vars(args))