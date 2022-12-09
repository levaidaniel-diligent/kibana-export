#!/bin/sh

API_KEY=${API_KEY:-''}
OUTPUT='-'

URL_NONPROD='https://kibana-nonprod.logs.diligent.com'
URL_PROD='https://kibana.logs.diligent.com'

while getopts 'k:e:o:h' opt;do
	case "${opt}" in
		o)
			OUTPUT="${OPTARG}"
			# safety 1st
			if [ -e "${OUTPUT}" ];then
				echo "'${OUTPUT}', file exists - won't overwrite!"
				exit 1
			fi
			;;
		k)
			API_KEY=${OPTARG}
			;;
		e)
			case "${OPTARG}" in
				'prod')
					URL=${URL_PROD}
					;;
				'nonprod')
					URL=${URL_NONPROD}
					;;
				*)
					echo "Unknown environment: ${OPTARG} - use 'prod' or 'nonprod'"
					exit 2
			esac
			;;
		h)
			echo "$0 -e <prod|nonprod> -k <API_KEY> [-o <OUTPUT_FILE>] [-h]"
			echo " -e <prod|nonprod> - Use specific Kibana URL based on the specified environment."
			echo " -k <API_KEY> - Kibana API key for authentication."
			echo " -o <OUTPUT_FILE> - File to write the export to. It won't overwrite existing files!"
			echo " -h - this help"
			exit 2
	esac
done

if [ -z "${URL}" ];then
	echo "Missing environment - specify 'prod' or 'nonprod' with '-e'"
	exit 2
fi

if [ -z "${API_KEY}" ];then
	echo "Missing API key - specify with '-k'"
	exit 2
fi


curl \
	--header 'Content-Type: application/json;charset=UTF-8' \
	--header 'kbn-xsrf: true' \
	--header "Authorization: ApiKey ${API_KEY}" \
	--request POST \
	--data '{ "type": "dashboard" }' \
	--output "${OUTPUT}" \
	"${URL}/api/saved_objects/_export"
