import json

from pyapollo import ApolloClient


def main():
    MODE = 'DEV'  # Different environment settings
    conf_file = 'connection_config.json'
    with open(conf_file) as fob:
        conn_config = json.load(fob)[MODE]

    srv_meta = conn_config['srv_meta']
    appId = conn_config['appId']
    clusterName = conn_config['clusterName']
    namespaceName = conn_config['namespaceName']
    secret = conn_config['secret']

    apollo_client = ApolloClient(srv_meta, appId, clusterName, secret)
    obj = apollo_client.get_namespace(namespaceName)
    print(type(obj), obj)

    obj = apollo_client.get_value('application', 'timeout')
    print('\n\n')
    print(type(obj), obj)

    obj = apollo_client.get_values('application')
    print('\n\n')
    print(type(obj), obj)


if __name__ == '__main__':
    main()
