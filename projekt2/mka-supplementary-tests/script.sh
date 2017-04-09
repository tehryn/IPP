for file in ./*.out
do
	echo "$file"
	echo "--------------------"
	diff ref-out/$file $file
	echo "===================="
done
for file in ./*.\!\!\!
do
	echo "$file"
	echo "--------------------"
	diff ref-out/$file $file
	echo "===================="
done
for file in ./*.err
do
	echo "$file"
	echo "--------------------"
	diff ref-out/$file $file
	echo "===================="
done
