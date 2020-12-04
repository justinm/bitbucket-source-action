from os.path import dirname, realpath

from aws_cdk import core, aws_codepipeline_actions as actions
from aws_cdk.aws_apigatewayv2 import HttpApi, PayloadFormatVersion
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_secretsmanager import Secret, SecretStringGenerator


class BitbucketSourceS3Action(core.Construct):
    def __init__(
            self,
            scope: core.Construct,
            construct_id: str,
            *,
            action_name: str,
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
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id)

        self.secret = Secret(scope, 'secret', generate_secret_string=SecretStringGenerator(password_length=secret_length))

        self.function = PythonFunction(self, 'lambda',
                                       entry=realpath(dirname(__file__)+"/function"),
                                       environment={
                                           "BITBUCKET_SERVER_URL": bitbucket_url,
                                           "BITBUCKET_TOKEN_ID": token.secret_name,
                                           "BITBUCKET_SECRET_ID": self.secret.secret_name,
                                           "PROJECT_NAME": project_name,
                                           "REPO_NAME": repo_name,
                                           "S3BUCKET": bucket.bucket_name,
                                           "S3PREFIX": bucket_key_prefix,
                                       })

        bucket.grant_read_write(self.function)
        self.secret.grant_read(self.function)

        notifications_integration = LambdaProxyIntegration(handler=self.function,
                                                           payload_format_version=PayloadFormatVersion.VERSION_1_0)

        self.api = HttpApi(scope, "http-api", default_integration=notifications_integration)

        if trigger:
            t = actions.S3Trigger.EVENTS
        else:
            t = actions.S3Trigger.NONE

        self.bucket_key = '%s/%s/%s/%s.zip' % (
            bucket_key_prefix,
            project_name,
            repo_name,
            branch
        )
        self.action = actions.S3SourceAction(
            bucket=bucket,
            bucket_key=self.bucket_key,
            output=output,
            action_name=action_name,
            trigger=t,
            **kwargs
        )

        core.CfnOutput(scope, 'bitbucket-notification-endpoint',
                       value="https://%s.execute-api.%s.amazonaws.com" % (self.api.http_api_id, scope.region))

        core.CfnOutput(scope, 'bitbucket-secret-arn', value=self.secret.secret_arn)
