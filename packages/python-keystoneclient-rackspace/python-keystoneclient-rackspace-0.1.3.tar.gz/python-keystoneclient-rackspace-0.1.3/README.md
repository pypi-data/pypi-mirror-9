# python-keystoneclient-rackspace
Plugin for API key authentication in the Rackspace Cloud

Example usage:

    from keystoneclient_rackspace.v2_0 import RackspaceAuth
    from keystoneclient.session import Session
    from novaclient.client import Client

    auth = RackspaceAuth(
        auth_url="https://identity.api.rackspacecloud.com/v2.0",
        username="demoauthor",
        api_key="aaaaa-bbbbb-ccccc-12345678",
        tenant_id=1100111)
    session = Session(auth=auth)
    client = Client(2, session=session, region_name="DFW")
    client.servers.list()
