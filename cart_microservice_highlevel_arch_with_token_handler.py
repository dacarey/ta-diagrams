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

from diagrams.aws.security import (
    Cognito as Curity,
    IdentityAndAccessManagementIamLongTermSecurityCredential as Authorizer,
    SecretsManager
)

from diagrams.aws.business import BusinessApplications as BusinessApplication

from diagrams.custom import Custom

from diagrams.aws.integration import Eventbridge, StepFunctions

from diagrams.onprem.network import Nginx

from diagrams.saas.identity import Auth0 as OAuthAgent


with Diagram(
    "Cart Service - High Level Architecture", 
    filename="cart_microservice_highlevel_arch_with_token_handler",
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

        dependent_apis = Cluster("Dependent\nAPIs")
        with dependent_apis:
            product_api = APIGatewayEndpoint("Product API")

    with Cluster("Website API Support"):
        oauth_suite = Cluster("Token Handler")

        with oauth_suite:
            oauth_agent = OAuthAgent("OAuth Agent")
            oauth_proxy = Nginx("OAuth Proxy")

            #  routes
            oauth_agent >> Edge(xlabel="Obtain Token", style="dashed") >> curity


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

        micro_service = Cluster("Core Commerce Proxy Micro Service")
        with micro_service:
            service_impl = Lambda("Service\nImplementation")
            secrets_manager = SecretsManager("Secrets\nManager")
            step_functions = StepFunctions("Express Workflow\nStep Functions")

            service = [service_impl, step_functions, secrets_manager]

            #  routes
            api_groups >> service_impl
            service_impl - Edge(xlabel="secrets", style="dashed") - secrets_manager
            service_impl - Edge(label="pipeline validations", style="dashed") - step_functions
            step_functions - Edge(xlabel="calls", style="dashed") - product_api

    with Cluster("Commerce Tools SAAS"):
        ct_service = Cluster("Commerce Tools")
        with ct_service:
            ct = Custom("CommerceTools", "./resources/commercetools-logo.png")

    #  routes
    netlify_website  >> Edge(xlabel="User\nLogin") >> oauth_agent
    oauth_agent >> Edge(xlabel="Secure\nCookie") >> netlify_website
   
    netlify_website >> Edge(label="API\nvia\nCookie") >>oauth_proxy >> Edge(label="API\nvia\nToken") >> me_api
    netlify_website >> Edge(xlabel="API\nvia\nToken") >> me_api
    grapevine >> stateless_api
    service_impl >> ct
    ct >> Edge(label="Fire\nEvents", style="dashed") >> event_bridge
