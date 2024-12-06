#!/bin/bash

echo "What is the AWS profile you would like to use?"
echo -n "AWS profile name: "
read -r aws_profile

echo "export AWS_PROFILE=$aws_profile" > .env

echo "Successfully saved your choices in .env file."
