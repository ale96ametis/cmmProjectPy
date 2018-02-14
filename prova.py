import numpy as np
f1 = open("prova.txt","r")
f2 = open("prova2.txt","r")

global testo1
global testo2

n=40 #righe matrice
m=136 #colonne matrice

array1 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file
array2 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file

check1 = np.zeros((m)) #array di controllo per il calcolo delle medie
check2 = np.zeros((m)) #array di controllo per il calcolo delle medie
ris = np.zeros((m)) #array contentente la sottrazione tra le medie calcolate

i=0 #indice per scorrere le righe della matrice
j=0 #indice per scorrere le colonne della matrice e degli array di controllo
k=0 #indice per scorrere le righe della matrice nell'inserimento dei dati negli array di controllo

c=1 #indica quale blocco di "l" righe considerare, quindi se le prime 5 righe, le seconde cinque e via cosi, viene incrementato nel codice
l=5 #numero di righe da confrontare per fare la media dei valori

while 1:
	testo1 = f1.readline()
	if testo1 == "":
		break
	testo2 = f2.readline()
	if testo2 == "":		
		break
	if int(testo1) == 1000: #testo=1000 = carattere di controllo che indice il fine riga dei marker
		i = i+1
		if i == n:
			break
		j=0
		testo1 = f1.readline()
		if testo1 == "":
			break
		testo2 = f2.readline()
		if testo2 == "":		
			break
	array1[i][j]=(int(testo1))
	array2[i][j]=(int(testo2))
	if i == c*l:	
		while k<i:
			while j<m:
				#inserisco all'interno degli array di check la somma dei valori desiderati
				check1[j]=check1[j]+array1[k][j]
				check2[j]=check2[j]+array2[k][j]
				j=j+1
			k=k+1
			j=0
		while j<m:
			#calcolo la media degli array di check
			check1[j]=check1[j]/l
			check2[j]=check2[j]/l
			ris[j]=check1[j]-check2[j]
			j=j+1
		j=0
		c=c+1	
	j=j+1

print (array1)
print (array2)
print (check1)
print (check2)
print (ris)

f1.close()
f2.close()

"""
with open('prova.txt') as f:
	data = [line.split() for line in f.readlines()]
	array1 = [(int(k), int(v)) for k, v in data]
with open('prova2.txt') as f:
	data = [line.split() for line in f.readlines()]
	array2 = [(int(k), int(v)) for k, v in data]

print (array1)
print (array2)
"""

