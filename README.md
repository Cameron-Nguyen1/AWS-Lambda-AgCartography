# AWS-Lambda-ANTIGENIC-CARTOGRAPHY
Antigenic Cartography pipeline deployed on AWS across Lambda and S3. This pipeline interfaces with another lambda function that serves a "dynamic" HTML.

# I. Introduction
To serve the laboratory's need for fast and accessible Antigenic Cartography, we have chosen to use Lambda to deploy a serverless implementation of Antigenic Cartography. A user will fill out of a webform, upload a CSV file for cartography, and then click "submit". Once submitted, a second lambda will asynchronously process the submitted CSV file. Upon a successful submission, the user will be presented with a 
different HTML page which presents a "request download" button. This new button creates a signed S3 URL to securely request the results of a user's submission.


# II. Details
The R container should be monitored for RAM usage, higher degrees of dimensionality will require more RAM.
#
This is an AWS implementation of the code found in the publicized work available at: https://github.com/Cameron-Nguyen1/N204_data_availability
#
There are three Lambda functions and they are as follows:
```
1. The Lambda that serves the DHTML with Python.
2. The Lambda that asynchronously performs Antigenic Cartography.
3. The Lambda that generates signed S3 urls for downloading results.
```
There are two S3 bucket involved. An input and an output bucket.
# III. Figures
## Figure 1.
Here's the landing page which is the initial web form.
![image](https://github.com/user-attachments/assets/ecf63dca-88ac-4a9d-8283-1656b8bbba45)
## Figure 2.
Here's an example of the cartography product:
![image](https://github.com/user-attachments/assets/54084a77-e8c7-4261-bd24-42cb52db51aa)
