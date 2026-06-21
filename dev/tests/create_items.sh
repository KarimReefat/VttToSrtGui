cd "t1"
i=1
while (( i++ < 900)); do
	mkdir -p "t$i"
	cd "t$i"
	cp ../"$(($i-1))".vtt "$i".vtt
	cp ../"$(($i-1))".vtt "a$i".vtt
	cp ../"$(($i-1))".vtt "aa$i".vtt
done
