#!/bin/bash

Suite_Folder="TestSuites"
ROBOT_OUTPUTDIR=output
rm -rf $ROBOT_OUTPUTDIR 2>/dev/null

mkdir ${ROBOT_OUTPUTDIR}
chmod 777 ${ROBOT_OUTPUTDIR}

# mandatory parameters
if [ -z "$PROFILE" ];
then
    echo "Profile parameter must be set!"
    exit 1
fi

if [ -z "$ROBOT_LOG_LEVEL" ];
then
    echo "Robot log level parameter must be set!"
    exit 1
fi

if [ -z "$FOLDER" ];
then
    echo "Folder parameter must be set!"
    exit 1
fi

number_regexp='^[0-9]\+$'
if [ "$RERUN" == true ] && [ -n "${RERUN_Limit}" ] && [ $(echo $RERUN_Limit|grep -cw $number_regexp) -ne 1 ];
then
	echo
	echo "Invalid input at RERUN_Limit parameter: \"${RERUN_Limit}\""
	echo
	exit 1
fi

ROBOTCMD="--variablefile profiles/$PROFILE --outputdir $ROBOT_OUTPUTDIR --noncritical NonCritical --loglevel $ROBOT_LOG_LEVEL --variable CLI_MODE:'TRUE'"

# optional parameters
if [ -n "$TA_ENV" ];
then
    # TA_ENV shall preceed PROFILE variable file
    ROBOTCMD="--variablefile profiles/$TA_ENV $ROBOTCMD"
fi

if [ -n "$EXCLUDED_TAGS" ];
then
    ROBOTCMD="$ROBOTCMD --exclude $EXCLUDED_TAGS"
fi

if [ -n "$INCLUDED_TAGS" ];
then
    ROBOTCMD="$ROBOTCMD --include $INCLUDED_TAGS"
fi

if [ -n "$TESTS" ];
then
	prepared_tests_string=""
	for word in $TESTS
	do
		if [ "$word" == "--test" ];
		then
			continue
		else
			prepared_tests_string+="--test $word "
		fi
	done
	#removes last whitespace
	prepared_tests_string=$(echo $prepared_tests_string|sed 's/ +$//g')
	ROBOTCMD="$ROBOTCMD $prepared_tests_string"
fi

if [ "$DRYRUN" == true ];
then
    ROBOTCMD="$ROBOTCMD --dryrun"
fi

if [ -n "${E2E_TA_Branch}" ] || [ -n "${E2E_CKW_Branch}" ] || [ -n "${SC_Suite_Branch}" ];
then
	git submodule update --init --recursive

	echo
	echo "##########################################"
	echo "# Switching to custom branch combitation #"
	echo "##########################################"
	echo
	
	if [ -z "${E2E_TA_Branch}" ] || [ "${E2E_TA_Branch}" == "" ];
	then
		echo "E2E-TA-Framework branch was not defined. Master branch will be used"
		E2E_TA_Branch="master"
	fi

	if [ -z "${SC_Suite_Branch}" ] || [ "${SC_Suite_Branch}" == "" ];
	then
		echo "${Suite_Folder} branch was not defined. Master branch will be used"
		SC_Suite_Branch="master"
	fi
    git submodule foreach git checkout master
    git submodule foreach git pull origin master
	TEMP_BRANCH_NAME="$1"
	
	localDir=$(pwd)

	git branch $TEMP_BRANCH_NAME
	git checkout $TEMP_BRANCH_NAME
	
	echo
	echo "Enter ${Suite_Folder} repository:"
	cd "${localDir}"
	cd ${Suite_Folder}
	git checkout ${SC_Suite_Branch}
	git pull 1> /dev/null

	echo
	echo "Enter E2E-TA-Framework repository:"
	cd "${localDir}"
	cd OSS-E2E-TA-Framework
	git checkout ${E2E_TA_Branch}
	git pull 1> /dev/null

	echo
	cd "${localDir}"
	
	modified_SC=$(git status|grep modified|grep "new commit"|grep -cw ${Suite_Folder})
	modified_TA=$(git status|grep modified|grep "new commit"|grep -cw OSS-E2E-TA-Framework)
	echo
	
	if [ "$modified_SC" == "1" ];
	then
		git add ${Suite_Folder}
		git commit -m "Updated ${Suite_Folder} submodule to ${SC_Suite_Branch}"
		echo
	fi
	
	if [ "$modified_TA" == "1" ];
	then
		git add OSS-E2E-TA-Framework
		git commit -m "Updated OSS-E2E-TA-Framework submodule to ${E2E_TA_Branch}"
		echo
	fi


	cd $localDir
	echo
	echo "Submodule states:"
	echo "-----------------"
	git submodule status
	
fi

ROBOTCMD="pybot $ROBOTCMD"

echo
echo "####################################"
echo "# Running solution container tests #"
echo "####################################"
echo
FIRST_RUN="$ROBOTCMD $FOLDER"
echo "Command to be executed: $FIRST_RUN"

if [ "$RERUN" == true ] && [ -n "${RERUN_Limit}" ] && [ $(echo $RERUN_Limit|grep -cw $number_regexp) -eq 1 ];
then
	eval $FIRST_RUN | tee ${ROBOT_OUTPUTDIR}/${TEMP_BRANCH_NAME}.txt
else
	eval $FIRST_RUN
	# we stop the script here if all the tests were OK
	if [ $? -eq 0 ];
	then
		echo
		echo "We don't run the tests again as everything was OK on first try."
		echo
		exit 0
	fi
fi

# otherwise we go for another round with the failing tests

if [ "$RERUN" == true ]
then
	if [ -n "${RERUN_Limit}" ] && [ $(echo $RERUN_Limit|grep -cw $number_regexp) -eq 1 ];
	then
		failed_critical_tc_number=$(grep -A2 -w ^"WAF\s\+|\s\+[FP]A[IS][LS]\s\+|" ${ROBOT_OUTPUTDIR}/${TEMP_BRANCH_NAME}.txt | awk '/critical test/ {print $6}')
		if [ ${failed_critical_tc_number} -eq 0 ];
		then
			echo "We don't run the tests again as everything was OK on first try."
			echo
			rm -fr ${ROBOT_OUTPUTDIR}/${TEMP_BRANCH_NAME}.txt
			exit 0
		elif [ ${failed_critical_tc_number} -ge ${RERUN_Limit} ];
		then
			echo
			echo "#####################################################################"
			echo "# Failed critical test cases exceeded the value of RERUN_Limit (${RERUN_Limit}) #"
			echo "# Re-run of the failed test cases will be skipped                   #"
			echo "#####################################################################"
			echo
			rm -fr ${ROBOT_OUTPUTDIR}/${TEMP_BRANCH_NAME}.txt
			exit 0
		else
			rm -fr ${ROBOT_OUTPUTDIR}/${TEMP_BRANCH_NAME}.txt
		fi
	fi

	RE_RUN="$ROBOTCMD --output rerun.xml --rerunfailed $ROBOT_OUTPUTDIR/output.xml $FOLDER"
	echo
	echo "#######################################"
	echo "# Running again the tests that failed #"
	echo "#######################################"
	echo
	if [ -n "$TESTS" ];
	then
		echo "##########################################################"
		echo "# Stripped the defined TCs to run only the failed one(s) #"
		echo "##########################################################"
		echo
		RE_RUN=$(echo $RE_RUN| sed 's/--test [a-Z0-9_-\*\?\+\#\(\)\{\}\\\/\!\`\~\#\@\%\&\=\;\:\|\<\>]* //g')
	fi
	echo "Command to be executed: $RE_RUN"
	eval $RE_RUN
	
	# Merging output files
	echo
	echo "########################"
	echo "# Merging output files #"
	echo "########################"
	echo
	rebot --noncritical NonCritical --outputdir $ROBOT_OUTPUTDIR --output output.xml --merge $ROBOT_OUTPUTDIR/output.xml $ROBOT_OUTPUTDIR/rerun.xml
fi