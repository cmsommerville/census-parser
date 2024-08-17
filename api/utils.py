from flask_restx import Api, Namespace
from typing import List


def bind_namespaces(api: Api, namespaces: List[Namespace], prefix: str = None) -> None:
    """
    Binds a list of API routes to the API object
    """
    for ns in namespaces:
        namespace = ns["namespace"]
        ns_path = ns.get("path")
        if ns_path.startswith("/"):
            ns_path = ns_path[1:]

        if ns_path.endswith("/"):
            ns_path = ns_path[:-1]
        api.add_namespace(namespace, path=f"{prefix}/{ns_path}")


def add_routes(namespace, routes):
    for route, resource in routes.items():
        namespace.add_resource(resource, route)
