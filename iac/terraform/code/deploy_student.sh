#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace # For debugging


##################################################

bash ./code/init.sh

start=$(date)
datetime=$(date "+%Y%m%d_%H%M%S")
mkdir -p .logs 

az account set --subscription $SUBSCRIPTION_ID
echo "use subscription ${SUBSCRIPTION_ID}" 

echo "terraform initializing..."
terraform -chdir=student init

for i in $(cat ./environments/${ENV}/student_rg_list.txt);
do
    student_logfile=".logs/iac_setup_student_${i}_${datetime}.log"
    if [ "${MODE}" = "plan" ];then
        echo "terraform plan for student_${i}..."
        terraform -chdir=student plan -var-file ../environments/${ENV}/student.tfvars -var rg_name=$i -state=./terraform_${i}.tfstate >>${student_logfile} 2>&1 &
    else
        echo "terraform apply student_${i}..."
        terraform -chdir=student apply --auto-approve -var-file ../environments/${ENV}/student.tfvars -var rg_name=$i -state=./terraform_${i}.tfstate >>${student_logfile} 2>&1 &
    fi
    sleep 10
done

end=$(date)

echo "Starting deployment at ${start}"
echo "finish deployment at ${end}"

