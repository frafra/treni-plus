#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import urlparse
from BeautifulSoup import BeautifulSoup
from jinja2 import Template
from flask import Flask

app = Flask(__name__)

url = 'http://mobile.viaggiatreno.it/vt_pax_internet/mobile/stazione'

colori = {
    '0':"success",
    '1':"warning",
    '2':"warning",
    '3':"danger",
    'c':"danger",
}

def make_links_absolute(soup, url):
    for tag in soup.findAll('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href'])
    return soup

def get_platform(div):
    br1, br2 = div.findAll('br')[1:3]
    strong = br2.findNextSibling('strong')
    if strong:
        return strong.text
    part2 = br2.next.split()
    if len(part2) > 2:
        if part2[2] != '--':
            return ' '.join(part2[2:])
    part1 = br1.next.split()
    if len(part1) > 2:
        return ' '.join(part1[2:])
    return '--'

def get_results(soup):
    res = []
    arrivo = False
    for div in soup.findAll('div'):
        if ('class', 'bloccorisultato') in div.attrs:
            codice = div.h2.text
            destinazione, orario = map(lambda tag: tag.text,
                div.findAll('strong'))[:2]
            img = div.find('img')
            ritardo = img.next if img else div.findAll('br')[-1].next
            res.append({
                'codice':codice,
                'destinazione':destinazione.title(),
                'orario':orario,
                'ritardo':ritardo.strip(),
                'binario':get_platform(div).lower(),
                'link':url+'/../'+div.a['href'],
                'colore':colori[div.img['src'][20]] if div.img else '',
                'arrivo':arrivo,
            })
        elif ('class', 'corpocentrale') in div.attrs:
            if div.text == 'Partenze':
                arrivo = False
            elif div.text == 'Arrivi':
                arrivo = True
    return res

with open('template/home.html', 'r') as template_file:
    template_home = Template(template_file.read().decode('utf8'))

with open('template/result.html', 'r') as template_file:
    template_result = Template(template_file.read().decode('utf8'))

@app.route('/')
def home():
    return template_home.render(titolo="Treni+ by Frafra",
        messaggio="Versione migliorata del ViaggiaTreno di Trenitalia")

@app.route('/<city>')
def timetable(city, code=False):
    if code:
        values = {
            'lang':'IT',
            'codiceStazione':city,
        }
    else:
        values = {
            'lang':'IT',
            'stazione':city,
        }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html)
    for span in soup.findAll('span'):
        if ('class', 'errore') in span.attrs:
            return template_result.render(titolo="Errore", messaggio=span.text)
    stazione = ' '.join(soup.find('h1').text.split()[2:]).title()
    treni = get_results(soup)
    if not treni:
        for select in soup.findAll('select'):
            if ('name', 'codiceStazione') in select.attrs:
                return timetable(select.find('option')['value'], code=True)
    return template_result.render(titolo="Stazione di "+stazione, treni=treni)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
