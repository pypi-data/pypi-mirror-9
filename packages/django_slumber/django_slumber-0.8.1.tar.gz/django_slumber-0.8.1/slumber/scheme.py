"""
    Utility functions for managing the slumber URL scheme.
"""
from slumber.server import get_slumber_services


class SlumberServiceURLError(Exception):
    """This exception is thrown if the Slumber URL has a service that does
    not match the service that it should have.
    """
    pass


def to_slumber_scheme(url, services=None):
    """Look at the URL and convert it to a service based URL if applicable.
    """
    if services is None:
        services = get_slumber_services()
    ret = None
    if services:
        longest = None, ''
        for service, service_url in services.items():
            if url.startswith(service_url) and len(service_url) > len(longest):
                ret, longest =  \
                    'slumber://%s/%s' % (service, url[len(service_url):]), \
                        service_url
    return ret or url


def from_slumber_scheme(url, services=None):
    """Turn a Slumber URL into a full URI as specified by the service
    configuration.
    """
    if services is None:
        services = get_slumber_services()
    if url.startswith('slumber://'):
        if not services:
            raise SlumberServiceURLError(
                "There are no services in the Slumber directory "
                "so the URL %s cannot be dereferenced" % url)
        for service in  services.keys():
            service_prefix = 'slumber://%s/' % service
            if url.startswith(service_prefix):
                service_url = services[service]
                final_url = service_url + url[len(service_prefix):]
                return final_url
        raise SlumberServiceURLError(
            "Service in URL %s not found in configured services %s"
                % (url, services.keys()))
    return url

