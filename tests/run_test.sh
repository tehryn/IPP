for file in ./*.\!\!\!
do
	echo -e "\n-----------------------------\n"
	cat $file
	echo -e "\n-----------------------------\n"
	cat ref-out/$file
	file=${file/\!\!\!/xml}
  	echo -e "\n-----------------------------\n"
        cat $file
        echo -e "\n-----------------------------\n"
        cat ref-out/$file
	echo -e "====================================\n"
done

