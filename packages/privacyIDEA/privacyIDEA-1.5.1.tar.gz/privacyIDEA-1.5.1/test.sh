#!/bin/bash
PRIV_PATH="privacyidea/tests/testdata"
export PYTHONPATH=.
STARTDATE=`date` 
NO_HTML=0
NO_COVERAGE=0
ADD_PARAM=""
for p in $*; do
	if [ "$p" == "--no-html" ]; then
		NO_HTML=1
	elif [ "$p" == "--no-coverage" ]; then
		NO_COVERAGE=1
	else
		ADD_PARAM="$ADD_PARAM $p"
	fi
done;



if [ "$NO_HTML" == "1" ]; then
	PARAM="-x"
else
	PARAM="-x --cover-html"
fi

if [ "$NO_COVERAGE" == "0" ]; then
	PARAM="$PARAM --with-coverage --cover-package=privacyidea"
fi

PARAM="$PARAM $ADD_PARAM"

rm -f /dev/shm/test-token.sqlite
killall paster
paster serve $PRIV_PATH/test.ini &

nosetests  $PARAM
RESULT=$?
killall paster
ENDDATE=`date` 
echo "We were running from $STARTDATE to $ENDDATE "
exit $RESULT
