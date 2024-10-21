from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds
)

import aws_cdk
from constructs import Construct

class CdkServerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, cdk_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        web_server_sg = ec2.SecurityGroup(self, "WebServerSG",
                                          vpc = cdk_vpc,
                                          allow_all_outbound = True,
                                          security_group_name = "WebServerSG",
                                          )
        
        web_server_sg.add_ingress_rule(
            peer = ec2.Peer.any_ipv4(),
            connection = ec2.Port.tcp(80),
            description = "Allow HTTP traffic"
        )
        
        InstanceRole = iam.Role(self, "InstanceSSM", assumed_by = iam.ServicePrincipal("ec2.amazonaws.com"))
        InstanceRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        instance_type = ec2.InstanceType("t2.micro")
        machine_image = ec2.MachineImage.latest_amazon_linux2()
        
        for i, subnet in enumerate(cdk_vpc.public_subnets, 1):
            ec2.Instance(self, f"WebServerInstance{i}",
                         vpc = cdk_vpc,
                         instance_type = instance_type,
                         machine_image = machine_image,
                         vpc_subnets = ec2.SubnetSelection(subnets = [subnet]),
                         security_group = web_server_sg,
                         role = InstanceRole,
                         key_name = "IaCLabKP"
                        )
        
        rds_sg = ec2.SecurityGroup(self, "RDSSecurityGroup",
                                   vpc = cdk_vpc,
                                   allow_all_outbound = True,
                                   security_group_name = "RDSSecurityGroup"
                                   )

        rds_sg.add_ingress_rule(
            peer = web_server_sg,
            connection = ec2.Port.tcp(3306),
            description = "Allow MySQL traffic from WebServerSG"
        )

        rds_instance = rds.DatabaseInstance(self, "RDSInstance",
                                             engine = rds.DatabaseInstanceEngine.mysql(
                                                 version = rds.MysqlEngineVersion.VER_8_0_39
                                             ),
                                             instance_type = ec2.InstanceType.of(
                                                 ec2.InstanceClass.BURSTABLE3,
                                                 ec2.InstanceSize.SMALL
                                             ),
                                             vpc = cdk_vpc,
                                             vpc_subnets = ec2.SubnetSelection(subnets = cdk_vpc.private_subnets),
                                             security_groups = [rds_sg],
                                             database_name = "mydb",
                                             deletion_protection = False,
                                             removal_policy = aws_cdk.RemovalPolicy.DESTROY
                                             )