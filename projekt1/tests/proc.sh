for file in ./*.xml
do
	cat $file
	echo -e "\n-----------------------------\n"
	cat ref-out/$file
	echo -e "\n=============================\n"
done
