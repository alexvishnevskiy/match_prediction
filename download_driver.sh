#!/bin/bash

output_file=chromedriver.zip
https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_mac64_m1.zip
https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip
curl --output $output_file https://chromedriver.storage.googleapis.com/96.0.4664.45/chromedriver_linux64.zip
unzip $output_file -d bins
rm $output_file
echo 'successfuly downloaded driver'