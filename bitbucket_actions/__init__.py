from os.path import dirname, realpath

from aws_cdk import core, aws_codepipeline_actions as actions
from aws_cdk.aws_apigatewayv2 import HttpApi, PayloadFormatVersion
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_secretsmanager import Secret, SecretStringGenerator


class BitbucketSourceS3Action(actions.S3SourceAction):
    def __init__(
            self,
            scope: core.Construct,
            bucket: Bucket,
            bitbucket_url: str,
            bucket_key_prefix: str,
            project_name: str,
            repo_name: str,
            token: Secret,
            output: Artifact,
            trigger: bool = True,
            secret_length: int = 24,
            branch: str = 'master',
    ) -> None:
        secret = Secret(scope, 'secret', generate_secret_string=SecretStringGenerator(password_length=secret_length))

        self.s3prefix = 'source/'+bucket_key_prefix
        function = PythonFunction(self, 'lambda',
                                  entry=realpath(dirname(__file__)+"/../functions/bitbucket-notifications"),
                                  environment={
                                      "BITBUCKET_SERVER_URL": bitbucket_url,
                                      "BITBUCKET_TOKEN_ID": token.secret_name,
                                      "BITBUCKET_SECRET_ID": secret.secret_name,
                                      "PROJECT_NAME": project_name,
                                      "REPO_NAME": repo_name,
                                      "S3BUCKET": bucket.bucket_name,
                                      "S3PREFIX": bucket_key_prefix,
                                  })

        bucket.grant_read_write(function)
        secret.grant_read(function)

        self.bucket = core.CfnOutput(scope, 'vcs-source-bucket-arn-output', value=bucket.bucket_arn,
                                     export_name='vcs-source-bucket-arn-output')

        notifications_integration = LambdaProxyIntegration(handler=function,
                                                           payload_format_version=PayloadFormatVersion.VERSION_1_0)

        api = HttpApi(scope, "http-api", default_integration=notifications_integration)

        core.CfnOutput(scope, 'webhook-url-output',
                       export_name='notification-webhook-url',
                       value="https://%s.execute-api.%s.amazonaws.com" % (api.http_api_id, scope.region))

        if trigger:
            t = actions.S3Trigger.EVENTS
        else:
            t = actions.S3Trigger.NONE

        super().__init__(
            action_name="Source",
            bucket=bucket,
            bucket_key='%s/%s/%s/%s.zip' % (
                bucket_key_prefix,
                project_name,
                repo_name,
                branch
            ),
            trigger=t,
            output=output,
        )