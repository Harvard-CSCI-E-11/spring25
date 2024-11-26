import boto3
import json
import logging

# Initialize AWS clients
s3_client = boto3.client('s3')
route53_client = boto3.client('route53')
ses_client = boto3.client('ses')

# Constants
HOSTED_ZONE_ID = "Z05034072HOMXYCK23BRA"  # Replace with your Route53 hosted zone ID
DOMAIN = "csci-e-11.org"  # Domain managed in Route53
SES_VERIFIED_EMAIL = "admin@csci-e-11.org"  # Verified SES email address

# Function to extract data from S3 object
def extract(content):
    (account_id, my_ip, email, name) = content.split(",")
    hostname = email.replace("@",".").split(".")[0]
    return hostname, my_ip, email

# Lambda handler
def lambda_handler(event, context):
    logging.info(f"Event received: {event}")

    # Get bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Get the content of the uploaded S3 object
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')

    # Extract data using the extract function
    hostname, ip_address, email = extract(content)

    # Create DNS record in Route53
    full_hostname = f"{hostname}.{DOMAIN}"
    route53_response = route53_client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": full_hostname,
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": ip_address}],
                    }
                }
            ]
        }
    )
    logging.info(f"Route53 response: {route53_response}")

    # Send email notification using SES
    email_subject = f"New DNS Record Created: {full_hostname}"
    email_body = f"""
    The following DNS record has been created:

    Hostname: {full_hostname}
    IP Address: {ip_address}

    Best regards,
    CSCIE-11 Team
    """
    ses_response = ses_client.send_email(
        Source=SES_VERIFIED_EMAIL,
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': email_subject},
            'Body': {'Text': {'Data': email_body}}
        }
    )
    logging.info(f"SES response: {ses_response}")

    return {
        "statusCode": 200,
        "body": json.dumps("DNS record created and email sent successfully.")
    }
