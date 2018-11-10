import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

import shared.config as cfg
from DBManagement import DatabaseManagement

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure Cosmos account - 
#    https://azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package - 
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Collection resource for Azure Cosmos
# 
# 1. Query for Collection
#  
# 2. Create Collection
#    2.1 - Basic Create
#    2.2 - Create collection with custom IndexPolicy
#    2.3 - Create collection with offer throughput set
#
# 3. Manage Collection Offer Throughput
#    3.1 - Get Collection performance tier
#    3.2 - Change performance tier
#
# 4. Get a Collection by its Id property
#
# 5. List all Collection resources in a Database
#
# 6. Delete Collection
# ----------------------------------------------------------------------------------------------------------
# Note - 
# 
# Running this sample will create (and delete) multiple DocumentContainers on your account. 
# Each time a DocumentContainer is created the account will be billed for 1 hour of usage based on
# the performance tier of that account. 
# ----------------------------------------------------------------------------------------------------------

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = cfg.settings['collection_id']

database_link = 'dbs/' + DATABASE_ID
collections_link ='dbs/' + DATABASE_ID + '/colls'

class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

class CollectionManagement:
    @staticmethod
    def find_Container(client, id):
        print('1. Query for specific Collection')

        collections = list(client.QueryContainers(
            database_link,
            {
                "query": "SELECT * FROM r WHERE r.id=@id",
                "parameters": [
                    { "name":"@id", "value": id }
                ]
            }
        ))

        if len(collections) > 0:
            print('Collection with id \'{0}\' was found'.format(id))
        else:
            print('No collection with id \'{0}\' was found'. format(id))

    # @staticmethod
    # def list_all_Containers(client):
    #     print('2. Query for Collections')

    #     collections = list(client.QueryContainers(collection_link)

    #     if len(collections) > 0:
    #         for c in collections: 
    #             print('Collection with id \'{0}\' was found'.format(c))
    #     else:
    #         print('No collection was found')

    @staticmethod
    def create_Container(client, id):
        """ The most basic Create of collection will create a collection with 400 RUs throughput and default automatic indexing policy          
         Our code will create a collection with custom index policy, custom offer throughput and unique keys     
         """

        print("Create Collection - With custom index policy, custom offer throughput and unique keys")
        
        try:
            coll = {            
                "id": id,    
                "indexingPolicy": {
                    "indexingMode": "lazy",
                    "automatic": False
                },
                "offerThroughput": 400,
                "uniqueKeyPolicy": {
                    "uniqueKeys": [{
                        'paths': ['/field1/field2', '/field3']
                    }]
                }
            }

            collection = client.CreateContainer(database_link, coll)
            unique_key_paths = collection['uniqueKeyPolicy']['uniqueKeys'][0]['paths']
            print('Collection with id \'{0}\' created'.format(collection['id']))
            print('IndexPolicy Mode - \'{0}\''.format(collection['indexingPolicy']['indexingMode']))
            print('IndexPolicy Automatic - \'{0}\''.format(collection['indexingPolicy']['automatic']))
           
            print('Collection with id \'{0}\' created'.format(collection['id']))
            print('Unique Key Paths - \'{0}\', \'{1}\''.format(unique_key_paths[0], unique_key_paths[1]))
            
        except errors.HTTPFailure as e:
            if e.status_code == 409:
               print('A collection with id \'{0}\' already exists'.format(collection['id']))
            else: 
                raise errors.HTTPFailure(e.status_code) 


    @staticmethod
    def manage_offer_throughput(client, id):
        print("\n3.1 Get Collection Performance tier")
        
        #A Collection's Offer Throughput determines the performance throughput of a collection. 
        #A Collection is loosely coupled to Offer through the Offer's offerResourceId
        #Offer.offerResourceId == Collection._rid
        #Offer.resource == Collection._self
        
        try:
            # read the collection, so we can get its _self
            collection_link = database_link + '/colls/{0}'.format(id)
            collection = client.ReadContainer(collection_link)
            # print('collection name \'{0}\''.format(collection))

            # now use its _self to query for Offers
            offer = list(client.QueryOffers('SELECT * FROM c WHERE c.resource = \'{0}\''.format(collection['_self'])))[0]
            
            print('Found Offer \'{0}\' for Collection \'{1}\' and its throughput is \'{2}\''.format(offer['id'], collection['_self'], offer['content']['offerThroughput']))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
                print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)

        print("\n3.2 Change Offer Throughput of Collection")
                           
        #The Offer Throughput of a collection controls the throughput allocated to the Collection
        #To increase (or decrease) the throughput of any Collection you need to adjust the Offer.content.offerThroughput
        #of the Offer record linked to the Collection
        
        #The following code shows how you can change Collection's throughput
        offer['content']['offerThroughput'] += 100
        offer = client.ReplaceOffer(offer['_self'], offer)

        print('Replaced Offer. Offer Throughput is now \'{0}\''.format(offer['content']['offerThroughput']))
                                
    @staticmethod
    def read_Container(client, id):
        print("\n Get a Collection by id")

        try:
            # All Azure Cosmos resources are addressable via a link
            # This link is constructed from a combination of resource hierachy and 
            # the resource id. 
            # Eg. The link for collection with an id of Bar in database Foo would be dbs/Foo/colls/Bar
            collection_link = database_link + '/colls/{0}'.format(id)

            collection = client.ReadContainer(collection_link)
            print('Collection with id \'{0}\' was found, it\'s _self is {1}'.format(collection['id'], collection['_self']))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)    
    
    @staticmethod
    def list_Containers(client, db):

        if  DatabaseManagement.find_database(client, db):
            print("\nList all collections in database \'{0}\'".format(db))               
            db_link = 'dbs/' + db
            collections = list(client.ReadContainers(db_link))            
            if not collections:
                print("\'{0}\' has no collections".format(db))
                return
            for collection in collections:
                print(collection['id'])          
        else:
            print("\'{0}\' not found".format(db))
            
    @staticmethod
    def delete_Container(client, id):
        print("\n6. Delete Collection")
        
        try:
           collection_link = database_link + '/colls/{0}'.format(id)
           client.DeleteContainer(collection_link)

           print('Collection with id \'{0}\' was deleted'.format(id))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)   
