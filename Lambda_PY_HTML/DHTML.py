import json
import boto3
from requests_toolbelt import MultipartDecoder
import logging
import base64
import io
import re
from botocore.exceptions import ClientError

logging.getLogger().setLevel(logging.INFO)

client_s3 = boto3.client('s3')


with open("index.html", 'r') as file:
    html = file.read()
    
def get_key(form_data):
    key = form_data.split(";")[1].split("=")[1].replace('"', '')
    return(key)
    
def object_exists(bucket_name, object_name,s3):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_name)
        return(True)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return(False)
        else:
            raise

def lambda_handler(event, context):
    logging.info('got event{}'.format(event))
    flag = 0
    try:
        z = event["requestContext"]["http"]["method"]
        flag = 1
    except:
        print("Event is irregular")
    finally:
        if flag == 1:
            if z == "POST":
                headers = event['headers']
                # decode the multipart/form-data request
                postdata = base64.b64decode(event['body'])
                
                request = {} # Save request here
                
                for part in MultipartDecoder(postdata, headers['content-type']).parts:
                    decoded_header = part.headers[b'Content-Disposition'].decode('utf-8')
                    key = get_key(decoded_header)
                    request[key] = part.content
                for k,v in request.items():
                    #print(k,v,sep=" : ")
                    if k == "fileup":
                        continue
                    request[k] = v.decode("utf-8")
                myfile = io.BytesIO(request["fileup"])
                df_str = io.TextIOWrapper(myfile, encoding='utf-8')
                df = "".join(df_str.read()) #This essentially prints all lines of the CSV, lets chock these print statements onto an empty string and combine the whole output to one strang!!!
                df = df.replace("\ufeff","")
                pattern_w = re.compile('[\W]')
                pattern_xy = re.compile('-\d+,\d+,-\d+,\d+')
                pattern_psize = re.compile('\d+,\d+')
                pattern_opacity = re.compile('(\d|\.\d),(\d|\.\d)')
                if not pattern_xy.match(request["limits"]):
                    request["limits"] = "-5,5,-5,5"
                if not pattern_psize.match(request["psize"]):
                    request["psize"] = "5,2"
                if not pattern_opacity.match(request["transparency"]):
                    request["transparency"] = ".8,1"
                if not request["Ag.Overprint"].upper() == "TRUE" and not request["Ag.Overprint"].upper() == "FALSE":
                    request["Ag.Overprint"] = "FALSE"
                if not request["Ag.Sort"].upper() == "TRUE" and not request["Ag.Sort"].upper() == "FALSE":
                    request["Ag.Sort"] = "TRUE"
                if request["outdir"] == "":
                    request["outdir"] = "DEFAULT_O"
                if request["prefix"] == "":
                    request["prefix"] = "DEFAULT_P"
                request["outdir"] = pattern_w.sub('', request["outdir"])
                request["prefix"] = pattern_w.sub('', request["prefix"])
                payload = {
                  "input": df,
                  "xy_lim": request["limits"],
                  "prefix": request["prefix"],
                  "out": request["outdir"],
                  "psizes": request["psize"],
                  "opacity": request["transparency"],
                  "agOverprint": request["Ag.Overprint"],
                  "agSort": request["Ag.Sort"]
                }
                key = request["outdir"]+"/payload.json"
                print("Submitting Put Object Request")
                client_s3.put_object(Body=json.dumps(payload).encode(),Bucket="YOURINPUTBUCKET",Key=key) #REPLACE
                newkey = request["outdir"]+".zip"
                if object_exists("YOUROUTPUTBUCKET", newkey,client_s3): #REPLACE
                    client_s3.delete_object(Bucket="YOUROUTPUTBUCKET", Key=newkey) #REPLACE
                rehtml = html.replace("IMAKEY", newkey)
                rehtml = rehtml.replace('{replaceme}','<button onclick="sign_and_download()">Submit Download Request</button>')
                response = {
                    "statusCode": 200,
                    "body": rehtml,
                    "headers": {
                        'Content-Type': 'text/html',
                    }
                }
            else:
                rehtml = html.replace('{replaceme}',z)
                response = {
                    "statusCode": 201,
                    "body": rehtml,
                    "headers": {
                        'Content-Type': 'text/html',
                    }
                }
        else:
            response = {
                "statusCode": 202,
                "body": html,
                "headers": {
                    'Content-Type': 'text/html',
                }
            }
        return(response)