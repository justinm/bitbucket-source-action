BitbucketSourceAction
=====================

An AWS CDK Construct for sourcing repositories from on-prem BitBucket instances.

Intended Audience
-----------------

This library is for users of Bitbucket On-Premise and AWS CodePipelines. This construct
adds BitbucketSourceAction for sourcing on-prem repositories.

Example
-----------

```python
from bitbucket_actions import BitbucketSourceS3Action

source = Artifact()
bucket = Bucket(self, 'source-bucket')
token = Secret.from_secret_arn(self, 'token', secret_arn='')

source_action = BitbucketSourceS3Action(
    scope, 
    'bitbucket',
    bucket=bucket, 
    bitbucket_url='https://bitbucket.internal'
    bucket_key_prefix='source/',
    project_name='',
    repo_name='',
    token=token,
    source=source
)

CdkPipeline(
    scope,
    account.name+'-cdk-pipeline',
    source_action=source_action.action,
    ...
)
```