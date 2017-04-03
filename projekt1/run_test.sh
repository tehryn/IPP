#!/bin/bash
if [ $# -eq 0 ]
then
	GREEN='\033[1;32m'
	RED='\033[1;31m'
	NC='\033[0m' # No Color
fi

prog="./proj1.php"

invalid=( "--help --help" "-l -l" )

for arg in ${invalid}
do
    tmp=$(${prog} ${arg} 2>&1)
    err=${?}
    if [[ ${err} == 1 ]]
    then
        echo -e "${GREEN}${prog} $arg${NC}"
    else
        echo -e "${RED}${prog} ${arg}${NC} returned with ${err} but should have returned with 1"
        echo -e "------------------------------------------------------------------------------------"
        printf "${tmp}"
        echo "===================================================================================="
    fi
done