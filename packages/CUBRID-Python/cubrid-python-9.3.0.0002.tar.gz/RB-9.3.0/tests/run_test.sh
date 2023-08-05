#!/bin/bash

result="tests.result"
touch $result

echo -e "Testing starts....."
echo -e "**********************************" > $result
echo -e "******Python Driver Unit Test*******" >> $result
echo -e "**********************************" >> $result
echo -e "\n" >> $result

i=1
for test_file in $(ls *.py); do
	echo -e "********$i. Test for $test_file ********" >> $result
	#run python to test all the unittests in the folder
	python $test_file
	sleep 1
	
	file_name=`echo "$test_file" | cut -d'.' -f1`
	cat $file_name.result >> $result
	echo -e "\n" >> $result
	
	rm $file_name.result
	i=`expr $i + 1`
done

rm out
echo -e "Testing ends....."
echo -e "See the test result file tests.result"