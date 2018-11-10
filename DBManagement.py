import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

import shared.config as cfg

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure Cosmos account - 
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos PyPi package - 
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure Cosmos
#
# Query for Database (QueryDatabases)
#
# Create Database (CreateDatabase)
#
# Get a Database by its Id property (ReadDatabase)
#
# List all Database resources on an account (ReadDatabases)
#
# Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------


HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']



class DatabaseManagement:
    @staticmethod
    def find_database(client, id):
        print('Query for Database')

        databases = list(client.QueryDatabases({
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }))

        if len(databases) > 0:
            print('Database with id \'{0}\' was found'.format(id))
            return True
        else:
            print('No database with id \'{0}\' was found'. format(id))
            return False
        
    @staticmethod
    def create_database(client, id):
        print("\n2. Create Database")
        
        try:
            client.CreateDatabase({"id": id})
            print('Database with id \'{0}\' created'.format(id))

        except errors.HTTPFailure as e:
            if e.status_code == 409:
               print('A database with id \'{0}\' already exists'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)               
    
    @staticmethod
    def read_database(client, id):
        print("\n3. Get a Database by id")

        try:
            # All Azure Cosmos resources are addressable via a link
            # This link is constructed from a combination of resource hierachy and 
            # the resource id. 
            # Eg. The link for database with an id of Foo would be dbs/Foo
            database_link = 'dbs/' + id

            database = client.ReadDatabase(database_link)
            print('Database with id \'{0}\' was found, it\'s _self is {1}'.format(id, database['_self']))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A database with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)    

    @staticmethod
    def list_databases(client):
        print("\n4. List all Databases on an account")
        
        print('Databases:')
        
        databases = list(client.ReadDatabases())
        
        if not databases:
            return

        for database in databases:
            print(database['id'])          

    @staticmethod
    def delete_database(client, id):
        print("\n5. Delete Database")
        
        try:
           database_link = 'dbs/' + id
           client.DeleteDatabase(database_link)

           print('Database with id \'{0}\' was deleted'.format(id))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A database with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)


# def print_menu():
#     print(30 * "-" , "MENU" , 30 * "-")
#     print("1. Query for a database")
#     print("2. Create a database")
#     print("3. Get a database using its id")
#     print("4. List all databases on an account")
#     print("5. Delete database by id")
#     print("6. Exit")
#     print(67 * "-")

# def run_sample():     
#     with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:
#         try:         
#             loop=True      
  
#             while loop:          ## While loop which will keep going until loop = False
#                 print_menu()    ## Displays menu
#                 choice = int(input("Enter your choice [1-6]: "))
                
#                 if choice == 1:     
#                     print("Menu 1 has been selected")
#                     DatabaseManagement.find_database(client, DATABASE_ID)
#                 elif choice == 2:
#                     print("Menu 2 has been selected")
#                     DatabaseManagement.create_database(client, DATABASE_ID)
#                 elif choice == 3:
#                     print("Menu 3 has been selected")
#                     DatabaseManagement.read_database(client, DATABASE_ID)
#                 elif choice == 4:
#                     print("Menu 4 has been selected")
#                     DatabaseManagement.list_databases(client)
#                 elif choice == 5:
#                     print("Menu 5 has been selected")
#                     DatabaseManagement.delete_database(client, DATABASE_ID)
#                 elif choice == 6:
#                     print("Menu 6 has been selected")
#                     ## You can add your code or functions here
#                     loop = false # This will make the while loop to end as not value of loop is set to False
#                 else:
#                     # Any integer inputs other than values 1-5 we print an error message
#                     input("Wrong option selection. Enter any key to try again..")

#             # query for a database
#             # DatabaseManagement.find_database(client, DATABASE_ID)
            
#             # create a database
#             # DatabaseManagement.create_database(client, DATABASE_ID)
                        
#             # get a database using its id
#             # DatabaseManagement.read_database(client, DATABASE_ID)

#             # list all databases on an account
#             # DatabaseManagement.list_databases(client)

#             # delete database by id
#             # DatabaseManagement.delete_database(client, DATABASE_ID)

#         except errors.HTTPFailure as e:
#             print('\nrun_sample has caught an error. {0}'.format(e.message))
        
#         finally:
#             print("\nrun_sample done")

# if __name__ == '__main__':
#     try:
#         run_sample()

#     except Exception as e:
#             print("Top level Error: args:{0}, message:{1}".format(e.args,e))