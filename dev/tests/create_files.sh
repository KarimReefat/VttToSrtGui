cd t1
for a in {2..600}
do 
	mkdir -p t$a
	cd t$a
	cp ../$(($a-1)).vtt ./$a.vtt
done
