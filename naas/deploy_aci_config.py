#!/usr/bin/env python3.8
import os
import csv
import json
import jinja2
import requests
import getpass
import re
import os.path, time

# Define file names of input j2 template, csv table, and output file
mycsvfile = 'data_input.csv'
mytemplatefile = 'config_template.j2'
myresultfile = 'aci_results.xml'

# CSV data_input.csv save time check
cur_time = time.time()  # current time
save_time = os.path.getmtime(mycsvfile)  # data_input.csv save time
if int(cur_time) - int(save_time) > 60:  # current time minus file saving time should be less than 60 seconds
    print("\n--- CSV data_input.csv was saved more than 60s ago on: ")
    print(time.ctime(save_time))
    print("\n--- Save data_input.csv file and run the script again\n")
    exit()

# Define regular expressions
num_pattern = re.compile('(^[0-9]*$)')  # matches numbers (digits) only
not_new_line_pattern = re.compile('.')  # matches anything but newline

# List of available fabric names
fabric_name_list = ['LAB']

# APIC IP for lab environment
apic_ip = "sandboxapicdc.cisco.com"

# CSV input file delimiter detection
with open(mycsvfile, 'rt') as file_in:
    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(file_in.read(5000)).delimiter
    print("\n--- CSV input file delimiter is '" + delimiter + "'")

# CSV input file data validation
print("\n--- Starting CSV input file data validation...")
with open(mycsvfile, 'rt') as file_in:
    temp_fn_list = []  # list to check if only one valid fabric name is added to the input file
    csvdata = csv.DictReader(file_in, delimiter=delimiter)

    # Going to count data rows with i
    i = 2
    for row in csvdata:
        dictforjinja = dict(fabricName=row.get('fabricName'),
                            podId=row.get('podId'),
                            nodeId=row.get('nodeId'),
                            Tenant=row.get('Tenant'),
                            AP=row.get('AP'),
                            EPG=row.get('EPG'),
                            vlan=row.get('vlan'),
                            mode=row.get('mode'),
                            fromPort=row.get('fromPort'),
                            toPort=row.get('toPort')
                            )

        # Empty fields (values)
        for key in dictforjinja:
            if len(dictforjinja['' + key + '']) == 0:
                print("\nIncorrect '" + key + "' value at row " + str(i) + ", can't be empty\n")
                exit()

# Credentials
usr = "admin"
pwd = "!v3G@!4@Y"

# Define URL and credentials for RESTAPI authentication
auth_url = "https://%s/api/aaaLogin.json" % apic_ip
headers = {'content-type': 'application/json'}
payload = {
    "aaaUser": {
        "attributes": {
            "name": usr,
            "pwd": pwd
        }
    }
}

# Suppress warnings when restapi uses https with self-signed certificate
requests.packages.urllib3.disable_warnings()

# Authenticate in APIC and save the security token
response = requests.post(auth_url, data=json.dumps(payload), headers=headers, verify=False, timeout=10)
print("\n--- AUTH response is %s" % response)
if response.status_code == 200:
    apic_auth_cookie = response.cookies
else:
    print("\n--- Username and/or password is incorrect")
    exit()

# Configuration
while True:
    ver = input("\nPress ENTER to start configuration process or type 'exit' to exit script: ").strip()
    if ver == 'exit':
        exit()
    elif not not_new_line_pattern.match(ver):
        break
    else:
        continue

# Read the j2 template
myjloader = jinja2.FileSystemLoader(os.getcwd())
myjenv = jinja2.Environment(loader=myjloader, trim_blocks=True, lstrip_blocks=True)
myjtemplate = myjenv.get_template(mytemplatefile)

# Read csv file row by row, process and write XML results to a file
with open(myresultfile, 'wt') as file_out:
    with open(mycsvfile, 'rt') as file_in:
        csvdata = csv.DictReader(file_in, delimiter=delimiter)
        i = 1
        for row in csvdata:
            dictforjinja = dict(podId=row.get('podId'),
                                nodeId=row.get('nodeId'),
                                Tenant=row.get('Tenant'),
                                AP=row.get('AP'),
                                EPG=row.get('EPG'),
                                vlan=row.get('vlan'),
                                mode=row.get('mode'),
                                fromPort=row.get('fromPort'),
                                toPort=row.get('toPort')
                                )
            if dictforjinja['mode'] == 'trunk':
                dictforjinja.update(mode='regular')
            if dictforjinja['mode'] == 'access':
                dictforjinja.update(mode='untagged')

            # Generate the XML payload
            myresult = myjtemplate.render(var=dictforjinja)

            # Print the generated XML for debugging
            print("Generated XML Payload:\n", myresult)

            # Save results to XML file
            file_out.write(myresult)
            file_out.write('\n\n---------------------\n\n')

            # Define POST url for RESTAPI, target the correct EPG object
            post_url = "https://%s/api/mo/uni/tn-%s/ap-%s/epg-%s.xml" % (apic_ip, dictforjinja['Tenant'], dictforjinja['AP'], dictforjinja['EPG'])

            # POST the XML result created from template and data from a CSV row
            headers = {'content-type': 'application/xml'}
            payload = myresult
            response = requests.post(post_url, data=payload, cookies=apic_auth_cookie, headers=headers, verify=False, timeout=5)

            # Print the response for more details
            print("POST response status code:", response.status_code)
            print("POST response content:", response.content.decode('utf-8'))

# Closing both input and output files
file_in.close()
file_out.close()

print("\n--- Finished running the script\n")