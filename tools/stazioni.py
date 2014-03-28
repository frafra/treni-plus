#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

url = "http://www.rfi.it/cms/v/index.jsp?vgnextoid=747e155031639210VgnVCM1000004016f90aRCRD"
html = urllib2.urlopen(url).read()
soup = BeautifulSoup(html)

regioni = []
for ul in soup.findAll('ul'):
    if ('id', 'menu3') in ul.attrs:
        for link in ul.findAll('a'):
            regioni.append(link['href'])

with open('stazioni.txt', 'w') as stazioni_file:
    stazioni = []
    for regione in regioni:
        html = urllib2.urlopen(regione).read()
        soup = BeautifulSoup(html)
        for cell in soup.findAll('td'):
            if ('scope', 'row') in cell.attrs:
               stazioni_file.write('<option value="')
               stazioni_file.write(cell.text.encode('utf8'))
               stazioni_file.write('"></option>\n')
