from gql import Client as GraphQLClient
from gql.transport.requests import RequestsHTTPTransport

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Client:
    def __init__(self, token):
        self.client = GraphQLClient(
            transport=RequestsHTTPTransport(
                url="https://api.github.com/graphql",
                use_json=True,
                headers={
                    "Content-type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                retries=3,
            )
        )

    def execute(self, query, variables):
        return self.client.execute(
            query,
            variable_values=variables,
        )
