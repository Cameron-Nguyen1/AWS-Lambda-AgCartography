# AWS_ANTIGENIC_CARTOGRAPHY
Antigenic Cartography pipeline deployed on lambda. This pipeline interfaces with another lambda function that serves a "dynamic" HTML.

This pipeline was designed to operate within the free tier of AWS Lambda usage. 
  If money were no object, a NAT gateway would eliminate the necessity to serve a download via dynamic HTML. The "Download Ready!" hypertext could be updated the moment it becomes available on S3, as opposed to updating upon submission which allows the user to      click an inactive link.
  
The R container should be monitored for RAM usage, higher degrees of dimensionality will require more RAM.

Here's a diagram of the intended workflow:
![image](https://github.com/user-attachments/assets/e4b483c0-27ab-4f86-89c8-386c922df567)
