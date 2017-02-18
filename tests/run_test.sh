#!/bin/bash
if [ $# -eq 0 ]
then
	GREEN='\033[1;32m'
	RED='\033[1;31m'
	NC='\033[0m' # No Color
fi

prog="../proj1.php"

invalid=array("--help --help" "-l -l")

for arg in $invalid
do
    $prog $arg
    if [[ $? == 1 ]]
    then
        echo -e "${GREEN}$prog $arg${NC}"
    else
        echo -e "${RED}${prog} ${arg}$NC"
done