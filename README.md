# CosmosDB-management-with-Python

Azure Cosmos Db – Python API – Working with databases, collections and documents
Pre-requisites 
•	Visual Studio Code
•	Python extension for Visual Studio Code 
•	Python 3.6 and references added in PATH https://www.python.org/downloads/
•	Azure CosmosDb account
All the code provided in this tutorial is available on GitHub:
git clone https://github.com/ron17ro/CosmosDB-management-with-Python.git
One of the supported APIs is the SQL API, which provides a JSON document model with SQL querying and JavaScript procedural logic. This tutorial shows how to use the Azure Cosmos DB with the SQL API to store and access data from a Python application.
If you don't have an Azure subscription, create a free account before you begin.
Try Azure Cosmos DB for free without an Azure subscription. Or, you can use the Azure Cosmos DB Emulator with a URI of https://localhost:8081. The Primary Key is provided in Authenticating requests.
You also need the Python SDK.
The application uses the Python API to perform CRUD operations on databases, collections and documents. A fair amount of code in this application was taken from https://github.com/Azure/azure-cosmos-python.git , however, all the methods were customized to fit the purpose of this tutorial.

The application structure and code review 
 
The configuration file shared/config.py
In order to set the connection details the following details are required in the configuration file:
settings = {
    'host': '[YOUR ENDPOINT]',
    'master_key': '[YOUR KEY]'
}
The endpoint and the connection key are displayed in the Azure CosmosDB account, under the menu “Keys”
 

The main class, used to run the application (ProgramMenu.py)
Contains a custom-made menu to easily perform actions on the Azure CosmosDB account.
$ python ProgramMenu.py
------------------------------ MENU ------------------------------
1. List all databases on an account
2. List all collections in specific database
3. Get a database by id
4. Get collection by id
5. Get & change collection Offer Throughput by 100
6. Create a database
7. Create a collection
8. Create documents
9. Read a specific document
10. Read all documents in a collection
11. Delete database by id
12. Delete collection by id
13. Exit
-------------------------------------------------------------------
Enter your choice [1-13]:

The connection to the database is done with the code below in the method run_sample()

with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:

Database management (DBManagement.py)
•	find_database(client, id) interrogates the system for a database using the  SQL syntax:
databases = list(client.QueryDatabases({
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }))

•	read_database(client, id) uses the URI of the resource, searching the database using the REST API. All Azure Cosmos resources are addressable via a link which is constructed from a combination of resource hierarchy and the resource id. Eg. The link for database with an id of FOO would be dbs/FOO
    database_link = 'dbs/' + id
    database = client.ReadDatabase(database_link)

•	create_database(client, id) will create a database using the python method client.CreateDatabase({"id": id}) and if a database with the same id exists, it will return a HTTP 409(Conflict) error.

•	list_databases(client) will list all available databases in the current account.

•	delete_database(client, id) is deleting the database name passed by the user in the console.  

Collection management (CollectionsManagement.py)
Working with containers will involve additional costs in a real environment (not trial). Each time a DocumentContainer is created, the account will be billed for 1 hour of usage based on the performance tier of that account. 
•	find_Container(client, db, id) in a similar way to working with databases, this method is searching a specific collection in a certain database using SQL. The database id and the collection name are provided by the user in the console.
       db_link = 'dbs/' + db
        collections = list(client.QueryContainers(
            db_link,
            {
                "query": "SELECT * FROM r WHERE r.id=@id",
                "parameters": [
                    { "name":"@id", "value": id } ]  }   ))

•	read_Container(client, db, id) takes 2 inputs from the console, the database name and the collection name. It uses the URI to search the existence of the collection.
db_link = 'dbs/' + db
collection_link = db_link + '/colls/{0}'.format(id)
collection = client.ReadContainer(collection_link)
print('Collection with id \'{0}\' was found, it\'s _self is {1}'.format(collection['id'], collection['_self']))

•	create_Container(client, db, id) it takes two parameters from the console, the database id where to create the collection and the collection name. The most basic create of collection will create a collection with 400 RUs throughput and default automatic indexing policy. This code will create a collection with custom index policy, custom offer throughput and unique keys  
try:
            coll = {            
                "id": id,    
                "indexingPolicy": {
                    "indexingMode": "lazy",
                    "automatic": False
                },
                "offerThroughput": 500,
                "uniqueKeyPolicy": {
                    "uniqueKeys": [{
                        'paths': ['/field1/field2', '/field3']
                    }]
                }
            }
            if DatabaseManagement.find_database(client, db):
                db_link = 'dbs/' + db
            else:
                return
            collection = client.CreateContainer(db_link, coll)
            unique_key_paths = collection['uniqueKeyPolicy']['uniqueKeys'][0]['paths']

The automatic indexing is set to false, the throughput is set to 500 RU instead of default 400 RU and unique keys are assigned to the new collection. 

•	manage_offer_throughput(client, db, id) this method takes two parameters from the console, database id and the collection id, it displays the available throughput and it increases the value with 100 RU. Collection's Offer Throughput determines the performance throughput of a collection. A Collection is loosely coupled to Offer through the Offer's offerResourceId
#Offer.offerResourceId == Collection._rid
     		 #Offer.resource == Collection._self
        
       
            # now use its _self to query for Offers using SQL
            offer = list(client.QueryOffers('SELECT * FROM c WHERE c.resource = \'{0}\''.format(collection['_self'])))[0]
            
            print('Found Offer \'{0}\' for Collection \'{1}\' and its throughput is \'{2}\''.format(offer['id'], collection['_self'], offer['content']['offerThroughput']))

The Offer Throughput of a collection controls the throughput allocated to the Collection. To increase (or decrease) the throughput of any Collection you need to adjust the Offer.content.offerThroughput of the Offer record linked to the Collection
        
        #The following code shows how you can change Collection's throughput
        offer['content']['offerThroughput'] += 100
        offer = client.ReplaceOffer(offer['_self'], offer)

•	list_Containers(client, db) takes as input the database name from the console and displays all available collections  
  db_link = 'dbs/' + db
                collections = list(client.ReadContainers(db_link))            
                if not collections:
                    print("\'{0}\' has no collections".format(db))
                    return
                for collection in collections:
                    print(collection['id'])          

•	delete_Container(client, db, id) takes two input values from the console: the database name and the collection id to be deleted.

   		 db_link = 'dbs/' + db
            		 collection_link = db_link + '/colls/{0}'.format(id)
              		 client.DeleteContainer(collection_link)

Document Management (DocumentManangement.py)
•	CreateDocuments(client, db, coll) takes two arguments from the consoles, the database id and the collection id where the documents will be created. The JSON definition is stored in 2 additional methods for simplicity GetSalesOrder(document_id) and GetSalesOrderV2(document_id)
db_link = 'dbs/' + db
                collection_link = db_link + '/colls/{0}'.format(coll)
                print('Creating Documents')

# Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
# This can be saved as JSON as is without converting into rows/columns.
                sales_order = DocumentManagement.GetSalesOrder("SalesOrder1")
                client.CreateItem(collection_link, sales_order)

•	ReadDocument(client, db, coll, doc_id) takes two arguments from the console, the database id and the collection id. The document name is specified in the code for simplicity. 

Note that Reads require a partition key to be specified. This can be skipped if your collection is not partitioned i.e. does not have a partition key definition during creation.

doc_link = collection_link + '/docs/' + doc_id
                response = client.ReadItem(doc_link)

                print('Document read by Id {0}'.format(doc_id))
                print('Account Number: {0}'.format(response.get('account_number')))

•	ReadDocuments(client, db, coll) takes two arguments from the console, the database id and the collection id. 
NOTE: Use MaxItemCount on Options to control how many documents come back per trip to the server. Important to handle throttles whenever you are doing operations such as this. Might result in a 429 (throttled request) error
	
documentlist = list(client.ReadItems(collection_link, {'maxItemCount':10}))                
              		 print('Found {0} documents'.format(documentlist.__len__()))                
               	 for doc in documentlist:
                   		print('Document Id: {0}'.format(doc.get('id')))
