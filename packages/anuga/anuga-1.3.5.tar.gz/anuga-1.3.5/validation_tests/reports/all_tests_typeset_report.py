#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="steve"
__date__ ="$13/03/2013 4:24:51 PM$"



import os

os.system('pdflatex -shell-escape  -interaction=batchmode all_tests_report.tex')
os.system('bibtex all_tests_report')
os.system('pdflatex -shell-escape  -interaction=batchmode all_tests_report.tex')
os.system('pdflatex -shell-escape  -interaction=batchmode all_tests_report.tex')

