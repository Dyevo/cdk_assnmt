from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkNetworkStack(Stack):
    
    @property
    def vpc(self):
        return self.cdk_vpc

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        self.cdk_vpc = ec2.Vpc(self, "cdk_vpc",
                        ip_addresses = ec2.IpAddresses.cidr("10.0.0.0/16"), max_azs = 2,
                        subnet_configuration = [ec2.SubnetConfiguration(cidr_mask = 24, name = "PublicSubnet", subnet_type = ec2.SubnetType.PUBLIC),
                                        ec2.SubnetConfiguration(cidr_mask = 24, name = "PrivateSubnet", subnet_type = ec2.SubnetType.PRIVATE_WITH_EGRESS),
                        ]
                )

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkAssnmtQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
