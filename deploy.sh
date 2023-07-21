#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
    cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] {staging, prod}

Deploys caim webapp to AWS App Runner by building the image, pushing to ECR, then running a migration.

AWS App Runner will automatically rebuild the service after ECR image changes.

Available options:

-h, --help      Print this help and exit
-v, --verbose   Print script debug info
-q, --quiet     Silence most messaging
EOF
    exit
}

cleanup() {
    trap - SIGINT SIGTERM ERR EXIT
    # script cleanup here
}

setup_colors() {
    if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
        NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
    else
        NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
    fi
}

msg() {
    [[ -z "${QUIET-}" ]] && echo >&2 -e "${1-}"
}

die() {
    local msg=$1
    local code=${2-1} # default exit status 1
    unset QUIET
    msg "${RED-}$msg${NOFORMAT-}"
    exit "$code"
}

parse_params() {
    while :; do
        case "${1-}" in
        -h | --help) usage ;;
        -v | --verbose) set -x ;;
        --no-color) NO_COLOR=1 ;;
        -q | --quiet) QUIET=1 ;;
        -?*) die "Unknown option: $1" ;;
      *) break ;;
        esac
        shift
    done

    args=("$@")

    # check required params and arguments
    [[ ${#args[@]} -eq 0 ]] && die "Missing script arguments - please provide an environment as only argument. staging or prod"
    environment=${args[0]}

    if [[ "staging prod" != *"${environment}"* ]];
    then
        die "Can only deploy to 'staging' or 'prod'"
    fi

    return 0
}


###########################
# Actual Script Execution #
###########################

parse_params "$@"
setup_colors

msg "${ORANGE}deploying to caim-app-${environment}!${NOFORMAT}!"
sleep 5
AWS_PROFILE=caim aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 324366619902.dkr.ecr.us-east-1.amazonaws.com
docker buildx build --platform linux/amd64 -t 324366619902.dkr.ecr.us-east-1.amazonaws.com/caim-app-staging:latest --push .
msg "${ORANGE} Applying database migrations to caim-app-${environment}!${NOFORMAT}!"
source ${environment}.env || die "Cannot find environment file ${environment}.env, no database migrations..."
sleep 5
python manage.py migrate
