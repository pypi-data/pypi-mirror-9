# coding: utf-8
[(div.find('span',class_='link').a.get('href'),div.find('span',class_='link').a.text) for div in divs if 'SUB' in div.text]
[(div.find('span',class_='link').a.get('href'),div.find('span',class_='link').a.text.split()[0]) for div in divs if 'SUB' in div.text]
get_ipython().magic(u'copy')
