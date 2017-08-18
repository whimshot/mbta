#!/usr/bin/env bash

GIT_DIR=`git rev-parse --git-dir 2> /dev/null`
if [ $? == 0 ]; then
		# Find the repo root and check for virtualenv name override
		GIT_DIR=`\cd $GIT_DIR; pwd`
		PROJECT_ROOT=`dirname "$GIT_DIR"`
		ENV_NAME=`basename "$PROJECT_ROOT"`
		if [ -f "$PROJECT_ROOT/.venv" ]; then
				ENV_NAME=`cat "$PROJECT_ROOT/.venv"`
		fi
		# Activate the environment only if it is not already active
		if [ "$VIRTUAL_ENV" != "$WORKON_HOME/$ENV_NAME" ]; then
				if [ -e "$WORKON_HOME/$ENV_NAME/bin/activate" ]; then
						workon "$ENV_NAME" && export CD_VIRTUAL_ENV="$ENV_NAME"
				fi
		fi
fi

autopep=$(autopep8 -dr .)

if [[ -z $autopep ]]
then
	echo "> PEP8 passed !"
else
	echo "> PEP8 DID NOT pass !"
	echo "$autopep" | colordiff
	exit 1
fi

`pytest -qq 2>&1 >/dev/null`
if [[ $? != 0 ]]
then
	echo "> Tests DID NOT pass !"
	exit 1
else
	echo "> Tests passed !"
fi

echo "Ready to push !"
exit 0
