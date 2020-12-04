BitbucketSourceAction
=====================

An AWS CDK Construct for sourcing repositories from on-prem BitBucket instances.

Intended Audience
-----------------

This library is for users of Bitbucket On-Premise and AWS CodePipelines. This construct
adds BitbucketSourceAction for sourcing on-prem repositories.

Installing
----------

```bash
pip3 install git+https://github.com/justinm/bitbucket-source-action.git
```

or add to your `requiremenets.txt`

```
-e git+https://github.com/justinm/bitbucket-source-action.git?master#egg=bitbucket_source_action
```

Example
-------

```python
from bitbucket_actions import BitbucketSourceS3Action

source = Artifact()
bucket = Bucket(self, 'source-bucket')
token = Secret.from_secret_arn(self, 'token', secret_arn='')

source_action = BitbucketSourceS3Action(
    scope, 
    'bitbucket',
    action_name='Source',
    bucket=bucket, 
    bucket_key_prefix='source/',
    bitbucket_url='https://bitbucket.internal',
    project_name='',
    repo_name='',
    token=token,
    output=source,
)

CdkPipeline(
    scope,
    account.name+'-cdk-pipeline',
    source_action=source_action.action,
    ...
)
```