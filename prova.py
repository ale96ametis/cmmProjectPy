import numpy as np
f1 = open("prova.txt","r")
f2 = open("prova2.txt","r")

global testo1
global testo2

n=100 #righe matrice
m=40 #colonne matrice

array1 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file
array2 = np.zeros((n,m)) #matrice per l'inserimento dei valori da file

i=0 #indice per scorrere le righe della matrice
j=0 #indice per scorrere le colonne della matrice e degli array di controllo
k=0 #indice per scorrere le righe della matrice nell'inserimento dei dati negli array di controllo
z=0 #indice per scorrere le righe dell'array di controllo

c=1 #indica quale blocco di "l" righe considerare, quindi se le prime 5 righe, le seconde cinque e via cosi, viene incrementato nel codice
l=5 #numero di righe da confrontare per fare la media dei valori
conta=0 #conta quanti valori vengono inseriti in media_tot
media_tot=0

check1 = np.zeros((int(n/l),m)) #array di controllo per il calcolo delle medie
check2 = np.zeros((int(n/l),m)) #array di controllo per il calcolo delle medie
ris = np.zeros((int(n/l),m)) #array contentente la sottrazione tra le medie calcolate

while 1:
	
	#leggo il contenuto dei file marker, esco se uno dei due file e' finito
	testo1 = f1.readline()
	if testo1 == "":
		break
	testo2 = f2.readline()
	if testo2 == "":		
		break
		
	#se raggiungo il carattere di controllo sono arrivato a "fine riga" dei marker
	if int(testo1) == 1000: #testo=1000 = carattere di controllo che indice il fine riga dei marker
		#passo alla riga successiva
		i = i+1
		#esco se sforo le dimensioni della matrice (posso ignorare gli ultimi marker)
		if i == n:
			break
			
		#se sono arrivato a fine riga marker riporto a zero la colonna della matrice -> j=0
		j=0
		#leggo i nuovi marker (quelli subito dopo il carattere di controllo)
		testo1 = f1.readline()
		
		#condizioni di uscita
		if testo1 == "":
			break
		testo2 = f2.readline()
		if testo2 == "":		
			break
	
	#salvo il contenuto dei file nelle matrici		
	array1[i][j]=(int(testo1))
	array2[i][j]=(int(testo2))
	
	if i == c*l:	
		while k<i:
			while j<m:
				#inserisco all'interno degli array di check la somma dei valori considerati
				check1[z][j]=check1[z][j]+array1[k][j]
				check2[z][j]=check2[z][j]+array2[k][j]
				j=j+1
			k=k+1
			j=0
			
		while j<m:
			if check1[z][j]==0:
				break
			#calcolo la media degli array di check
			check1[z][j]=check1[z][j]/l
			check2[z][j]=check2[z][j]/l
			ris[z][j]=check1[z][j]-check2[z][j] #array con le medie dei diversi valori
			media_tot=media_tot+abs(ris[z][j]) #media complessiva dell'array ris
			conta=conta+1 #conta quanti valori sono stati inseriti in media_tot
			j=j+1
		z=z+1	
		#riporto j a 0, verra' subito incrementata a 1 ma questo e' ok perche' ho gia' salvato array[i][0] (vedi sopra)
		j=0
		#incremento il controllo sulle righe da considerare
		c=c+1	
	j=j+1
	
media_tot=media_tot/conta

#print (array1)
#print (array2)
#print (check1)
#print (check2)
#print (ris)
print ("media tot:",media_tot)

if media_tot < 5:
	print ("lettura corretta")
if media_tot > 5 and media_tot < 10:
	print ("lettura con possibilità di qualche piccolo errore")
if media_tot > 10 and media_tot < 15:
	print ("lettura con probabile presenza di errori")
if media_tot > 15:
	print ("lettura contenente evidenti errori")

f1.close()
f2.close()

