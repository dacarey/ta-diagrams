"""
This module uses the diagrams library to generate a diagram
representing a high-level architecture of a microservice. 
"""
# pylint: disable=pointless-statement.
# - Pylint doesn't understand the >> operator in the context of the diagrams library.

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway, APIGatewayEndpoint
from diagrams.aws.database import Dynamodb
from diagrams.aws.security import (
    Cognito as Curity,
    IdentityAndAccessManagementIamLongTermSecurityCredential as Authorizer,
)
from diagrams.aws.business import BusinessApplications as BusinessApplication
from diagrams.custom import Custom

with Diagram(
    "Micro Service - High Level Architecture", filename="ms_high_level_arch", show=True
):
    with Cluster("Applications"):
        netlify_website = Custom("Website", "./resources/netlify_logo.png")

        grapevine = BusinessApplication("Grapevine")

    with Cluster("Identity\nManagement"):
        curity = Curity("OAuth")

    with Cluster("Website API Support"):
        webapi_suite = Cluster("webapi")
        with webapi_suite:
            webapi = APIGatewayEndpoint("Web API")

    with Cluster("AWS Micro Service"):
        api_gateway = Cluster("api.directwines.com")
        with api_gateway:
            me_api = APIGateway("ME\nendpoints")
            authorizer = Authorizer("Global\nAuthorizer")
            stateless_api = APIGateway("STATELESS\nendpoints")
            api_groups = [me_api, authorizer, stateless_api]

        with Cluster("Service"):
            service_impl = Lambda("Service\nImplementation")
            serviceStorage = Dynamodb("Service\nStorage")
            service = [service_impl, serviceStorage]

            api_groups >> service_impl >> serviceStorage

    netlify_website >> webapi >> me_api
    me_api - Edge(color="firebrick", style="dotted") - authorizer

    grapevine >> stateless_api
    stateless_api - Edge(color="firebrick", style="dotted") - authorizer

    authorizer >> curity
