cd "t1"
i=1
while (( i++ < 900)); do
	cd "t$i"
	rm -f *.srt
done
