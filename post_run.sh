#!/bin/bash

artifact_file="build.zip"
ROBOT_OUTPUTDIR=output

#If output.xml is not created, it means there was no test according to filtering criterias
is_output_xml_created=$(ls ./${ROBOT_OUTPUTDIR}/output.xml 2>/dev/null|wc -l)

if [ "${is_output_xml_created}" != "1" ];
then
    echo
    echo "*** There was no test case which matched to the selected criterias. Post run operations have been skipped. ***"
    echo
    exit 1
fi

if [ $# -eq 1 ];
then
	FINAL_LOG_LOCATION=$1

	echo "Final place of current run logs: ${FINAL_LOG_LOCATION}"
	mkdir -p ${FINAL_LOG_LOCATION}
	chmod 777 ${FINAL_LOG_LOCATION}
fi

echo
cd ${ROBOT_OUTPUTDIR}
#if [ "${DRYRUN}" == true ];
#then
echo "Adding files to ${artifact_file}:"
zip ${artifact_file} *ml
echo
#fi

if [ $# -eq 1 ];
then
	job_name=$(basename $(dirname ${FINAL_LOG_LOCATION}))
	build_number=$(basename ${FINAL_LOG_LOCATION})
	sed -i -e "s/\/var\/lib\/jenkins\/workspace\/${job_name}/\./g;s/\.\/${ROBOT_OUTPUTDIR}/\./g" *ml
	tar --exclude=build.zip -cvzf ${FINAL_LOG_LOCATION}/${job_name}_#${build_number}.tar.gz * 1>/dev/null
	operation_rc=$?
	if [ ${operation_rc} -eq 0 ];
	then
		echo "Log files successfully copied and gzipped to ${FINAL_LOG_LOCATION} (${operation_rc})"
	else
		echo
		echo "################################"
		echo "# Copy of log files failed (${operation_rc}) #"
		echo "################################"
		echo
	fi
fi
echo

