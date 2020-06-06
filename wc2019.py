#!/usr/bin/python3.6

import requests as r
from bs4 import BeautifulSoup
import sys 

timeout=5
dolist=0

subtable={}
tgenre="women"
tname="jpn"

if len(sys.argv)==1:
    url="https://wc2019.jva.or.jp/team/{0}/{1}.html".format(tgenre,tname)
else:
    if sys.argv[1] == 'list':
        dolist=1
        if len(sys.argv) > 2:
            tgenre=str(sys.argv[2].lower())
        url="https://wc2019.jva.or.jp/team/{0}.html".format(tgenre)
    else:
        if len(sys.argv) >= 2:
            tname=str(sys.argv[1].lower()) 
        if len(sys.argv) >= 3:
            tgenre=str(sys.argv[2].lower())
            if tgenre not in ["men","women"]:
                print("Une equipe doit etre genre men ou women")
                exit()
        print("Equipe utilisee : {0} {1}".format(tname,tgenre))
        url="https://wc2019.jva.or.jp/team/{0}/{1}.html".format(tgenre,tname)

def get_raw_html(url):
    try:
        raw=r.get(url,timeout=timeout)
    except r.exceptions.Timeout:
        print("Le site n'a pas repondu en {0} secondes".format(timeout))
        exit(8)
    if not raw.status_code == 200:
        print("Erreur durant la requete (code {0})".format(raw.status_code))
        print("Verifiez que le pays exist avec l'argument list")
        print(url)
        exit(9)
    return(raw)

def extract_table(input_data,ident=0):
    soup = BeautifulSoup(input_data.text,'html.parser')
    tables = soup.find_all('table')
    for i,j in enumerate(tables):
        subtable[i]=j
    table=subtable[0]
    return(table)

def make_list_with_table(table,tag="td",sub=""):
    if sub != "":
        table=table.find_all(sub)[0]
    all_lines=table.find_all('tr')
    outdict=[]
    for line in all_lines:
        this=line.find_all(tag)
        #print(this)
        foundel=[]
        for el in this:
            foundel.append(el.string)
        outdict.append(foundel)
    return(outdict)

def display_team(team,avg=1,avgonly=0):
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
    if avg == 1:
        print("La moyenne de taille est : {0} cm".format(moyenne))

raw=get_raw_html(url)
team=extract_table(raw)
if dolist == 1:
    country=make_list_with_table(team,'th',"tbody")
    #print(country)
    exit()

thisteam=make_list_with_table(team)
display_team(thisteam)
