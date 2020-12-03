import hashlib
import hmac
import json
import os
import boto3

from requests import get

secretsmanager = boto3.client('secretsmanager')
s3 = boto3.client('s3')


def handler(event, context):
    print('Event Received: '+json.dumps(event))

    try:
        body = json.loads(event['body'])
        headers = normalize_object(event['headers'])

        if 'x-event-key' in headers and headers['x-event-key'] == 'diagnostics:ping':
            return generate_response(200, 'Webhook configured successfully')

        secret = secretsmanager.get_secret_value(SecretId=os.getenv('BITBUCKET_SECRET_ID'), VersionStage="AWSCURRENT")
        token = secretsmanager.get_secret_value(SecretId=os.getenv('BITBUCKET_TOKEN_ID'), VersionStage="AWSCURRENT")

        if not (check_signature(secret, headers['x-hub-signature'], event.body)):
            print('Invalid webhook message signature')
            return generate_response(401, 'Signature is not valid')

        if body.changes[0].ref.type != 'BRANCH':
            print('Invalid event type')
            return generate_response(400, 'Invalid event type')

        repo_config = {
            'serverUrl': os.getenv('BITBUCKET_SERVER_URL'),
            's3prefix': os.getenv('S3PREFIX'),
            'projectName': body.repository.project.key,
            'repoName': body.repository.name,
            'branch': body.changes[0].ref.displayId,
            'token': token,
        }

        if repo_config['projectName'] != os.getenv('PROJECT_NAME'):
            print('Project name was invalid: %s !== %s' % (repo_config['projectName'], os.getenv('PROJECT_NAME')))
            return generate_response(400, 'Invalid project name')

        if repo_config['repoName'] != os.getenv('REPO_NAME'):
            print('Repository name was invalid: %s !== %s' % (repo_config['repoName'], os.getenv('REPO_NAME')))
            return generate_response(400, 'Invalid repository')

        file = download_file_from_bitbucket(repo_config)

        s3.put_object(
            Bucket=os.getenv('S3BUCKET'),
            ServerSideEncryption='AES256',
            Body=file.raw,
            Key='%s/%s/%s/%s.zip' % (repo_config['s3prefix'], repo_config['projectName'], repo_config['repoName'], repo_config['branch']),
        )

        return generate_response(200, 'success')
    except:
        return generate_response(500, 'Some weird thing happened')


def download_file_from_bitbucket(repo_config):
    url = '%s/rest/api/latest/projects/%s/repos/%s/archive?at=refs/heads/%s&format=zip' % \
          (repo_config['serverUrl'], repo_config['projectName'], repo_config['repoName'], repo_config['branch'])

    response = get(url, stream=True, headers={
        'Authorization': 'Bearer ' + repo_config['token']
    })

    return response


def normalize_object(input_object):
    """Convert an object keys to lowercase"""

    output = {}
    for key in input_object.keys():
        output[key.lower()] = input_object[key]

    return output


def generate_response(status_code: int, data):
    if status_code == 200:
        body = {
            'status_code': status_code,
            'message': data
        }
    else:
        body = {
            'status_code': status_code,
            'error': data
        }

    response = {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        }
    }

    return response


def check_signature(secret: str, signature: str, body) -> bool:
    signature_hash = hmac.new(
        bytes(secret, 'utf-8'),
        msg=bytes(body, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if signature_hash == signature.split('=')[1]:
        return True

    return False
