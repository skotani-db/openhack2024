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
terraform -chdir=trainer init

# trainer
trainer_logfile=".logs/iac_setup_trainer_${datetime}.log"

if [ "${MODE}" = "plan" ];then
    echo "terraform plan for trainer..."
    terraform -chdir=trainer  plan -var-file ../environments/${ENV}/trainer.tfvars -state=./terraform_trainer.tfstate >>${trainer_logfile} 2>&1
    
else
    echo "terraform apply for trainer..."
    terraform -chdir trainer apply --auto-approve -var-file ./environments/${ENV}/trainer.tfvars -state=./terraform_trainer.tfstate >>${trainer_logfile} 2>&1
fi

end=$(date)

echo "Starting deployment at ${start}"
echo "finish deployment at ${end}"

