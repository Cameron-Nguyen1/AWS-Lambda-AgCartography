# AWS-Lambda-ANTIGENIC-CARTOGRAPHY
Antigenic Cartography pipeline deployed on AWS across Lambda and S3. This pipeline interfaces with another lambda function that serves a "dynamic" HTML.

## I. Introduction
This pipeline was designed to operate within the free tier of AWS Lambda usage. 
If money were no object, a NAT gateway would eliminate the necessity to serve a download via dynamic HTML. The "Download Ready!" hypertext could be updated the moment it becomes available on S3, as opposed to updating upon submission which allows the user to      click an inactive link.

## II. Details
The R container should be monitored for RAM usage, higher degrees of dimensionality will require more RAM.
#
This is an AWS implementation of the code found in the publicized work available at: https://github.com/Cameron-Nguyen1/N204_data_availability

## Figure 1.
Here's an example of the cartography product:
![image](https://github.com/user-attachments/assets/54084a77-e8c7-4261-bd24-42cb52db51aa)
