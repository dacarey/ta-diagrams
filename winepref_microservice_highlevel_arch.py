"""

This module uses the diagrams library to generate a diagram

representing a high-level architecture of a microservice. 
"""

# pylint: disable=pointless-statement.

# pylint: disable=expression-not-assigned.

# - Pylint doesn't understand the >> operator in the context of the diagrams library.


from diagrams import Cluster, Diagram, Edge

from diagrams.aws.compute import Lambda

from diagrams.aws.network import APIGateway, APIGatewayEndpoint

from diagrams.aws.database import Dynamodb

from diagrams.aws.security import (
    Cognito as Curity,
    IdentityAndAccessManagementIamLongTermSecurityCredential as Authorizer,
    SecretsManager
)

from diagrams.aws.business import BusinessApplications as BusinessApplication

from diagrams.custom import Custom

from diagrams.aws.integration import Eventbridge


with Diagram(
    "Wine Preferences - High Level Architecture",
    filename="winepref_microservice_highlevel_arch",
    show=False
):
    with Cluster("Applications"):
        netlify_website = Custom("Website", "./resources/netlify-logo.png")

        grapevine = BusinessApplication("Grapevine")

    with Cluster("Identity Management"):
        cidm_suite = Cluster("CIDM")
        with cidm_suite:
            curity = Curity("Curity")
            scm_api = APIGatewayEndpoint("SCM - Scope\nto Claims\nMapping")

            #  routes
            curity >> scm_api

    with Cluster("Service Integration"):
        eventbridge_suite = Cluster("Event Bridge\nMessaging")
        with eventbridge_suite:
            event_bridge = Eventbridge("Event Bridge\nService")

    with Cluster("Website API Support"):
        webapi_suite = Cluster("webapi")

        with webapi_suite:
            webapi = APIGatewayEndpoint("Web API")

            #  routes
            webapi >> Edge(xlabel="Obtain Token", style="dashed") >> curity


    with Cluster("AWS Micro Service"):
        api_gateway = Cluster("API Gateway")

        with api_gateway:
            me_api = APIGateway("ME\nendpoints")
            authorizer = Authorizer("Global\nAuthorizer")
            stateless_api = APIGateway("STATELESS\nendpoints")

            api_groups = [me_api, stateless_api]

            #  routes
            authorizer >> Edge(xlabel="Introspect Token", style="dashed") >> curity
            stateless_api >> Edge(xlabel="Authorise\nToken", style="dashed") >> authorizer
            me_api >> Edge(xlabel="Authorise\nToken", style="dashed") >> authorizer

        micro_service = Cluster("Service")
        with micro_service:
            service_impl = Lambda("Service\nImplementation")
            dynamodb_storage = Dynamodb("Dynamo DB\nStorage")
            secrets_manager = SecretsManager("Secrets\nManager")

            service = [service_impl, dynamodb_storage, secrets_manager]

            #  routes
            api_groups >> service_impl >> dynamodb_storage
            service_impl - Edge(xlabel="secrets", style="dashed") - secrets_manager
            dynamodb_storage >> Edge(label="Fire\nEvents", style="dashed") >> event_bridge

    #  routes
    netlify_website >> webapi >> me_api
    grapevine >> stateless_api
