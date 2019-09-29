#!/usr/bin/python3.6

import requests as r
from bs4 import BeautifulSoup
import sys 

timeout=5
tname="jpn"

subtable={}

if len(sys.argv) > 1:
    tname=sys.argv[1] 

print("Equipe utilisee : ",str(tname))

url='https://wc2019.jva.or.jp/team/women/'+str(tname)+'.html'

try:
    raw=r.get(url,timeout=timeout)
except r.exceptions.Timeout:
    print("Le site n'a pas repondu en {0} secondes".format(timeout))
    exit(8)

if not raw.status_code == 200:
    print("Erreur durant la requete (code {0})".format(raw.status_code))
    exit(9)

soup = BeautifulSoup(raw.text,'html.parser')
tables = soup.find_all('table')
for i,j in enumerate(tables):
    subtable[i]=j
team=subtable[0]
all_lines=team.find_all('tr')
thisteam=[]
for line in all_lines:
    this=line.find_all('td')
    senshu=[]
    for el in this:
        senshu.append(el.string)
    thisteam.append(senshu)

#print(thisteam)
total=0
count=0
for i in thisteam:
    if i == []:
        continue
    if i[0][0] == 'C':
        i[0]=i[0][1:]
        print("{0:25} numero {1:4} mesure {2} (Capitaine)".format(i[2],i[0],i[8]))
    else: 
        print("{0:25} numero {1:4} mesure {2}".format(i[2],i[0],i[8]))
    total+=int(i[8])
    count+=1
moyenne=total/count
print("La moyenne de taille est : {0} cm".format(moyenne))
