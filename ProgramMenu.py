import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

import shared.config as cfg
from DBManagement import DatabaseManagement
from CollectionManagement import CollectionManagement
from DocumentManagement import DocumentManagement

# Create a custom menu for CosmosDB management 
# Database CRUD operations
# Collections CRUD operations

# ------------------------------ MENU ------------------------------
# 1. List all databases on an account
# 2. List all collections in specific database
# 3. Get a database by id
# 4. Get collection by id
# 5. Get & change collection Offer Throughput by 100
# 6. Create a database
# 7. Create a collection
# 8. Delete database by id
# 9. Delete collection by id
# 12. Exit
# -------------------------------------------------------------------
# Enter your choice [1-12]:


HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']

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
    
def print_menu():
        print(30 * "-" , "MENU" , 30 * "-")
        print("1. List all databases on an account")
        print("2. List all collections in specific database")
        print("3. Get a database by id")
        print("4. Get collection by id")
        print("5. Get & change collection Offer Throughput by 100")
        print("6. Create a database")
        print("7. Create a collection")
        print("8. Create documents")
        print("9. Read a specific document")
        print("10. Read all documents in a collection")
        print("11. Delete database by id")
        print("12. Delete collection by id")

        print("13. Exit")
        print(67 * "-")


def run_sample():     
        with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:
            try:         
                loop=True      
    
                while loop:          ## While loop which will keep going until loop = False
                    print_menu()    ## Displays menu
                    choice = int(input("Enter your choice [1-13]: "))
                    
                    if choice == 1:     
                        print("Menu 1 has been selected")
                        DatabaseManagement.list_databases(client)
                        
                    elif choice == 2:
                        print("Menu 2 has been selected")
                        # list all collection on an database
                        db_name = str(input("Please provide a database name: "))
                        if db_name:
                            CollectionManagement.list_Containers(client, db_name)
                        else:
                            print("Null string provided")
                    
                    elif choice == 3:
                        print("Menu 3 has been selected")
                        db_name = str(input("Please provide a database name: "))
                        if db_name:
                            DatabaseManagement.find_database(client, db_name)
                        else:
                            print("No input was provided")
                    elif choice == 4:
                        print("Menu 4 has been selected")
                        # query for a collection by id      

                        coll = str(input("Please provide a collection name: "))
                        if coll:
                            CollectionManagement.find_Container(client, coll)
                        else:
                             print("Empty name provided")

                        #  print("Menu 1 has been selected")
                        # DatabaseManagement.find_database(client, DATABASE_ID)
                    elif choice == 5:
                        print("Menu 5 has been selected")
                        coll = str(input("Please provide a collection name: "))  
                        if coll:
                            # get & change Offer Throughput of collection
                            CollectionManagement.manage_offer_throughput(client, coll)
                        else:
                             print("Empty name provided")
                        
                    elif choice == 6:
                        print("Menu 2 has been selected")
                        db_name = str(input("Please provide a database name to be created: "))
                        if db_name:
                            DatabaseManagement.create_database(client, db_name)
                        else:
                            print("Null value provided")
                    elif choice == 7:
                        print("Menu 7 has been selected")
                        # create a collection        
                        db_name = str(input("Please provide the database where the collection will be created: "))
                        coll_name = str(input("Please provide a collection name to be created: "))
                        if (len(db_name) != 0 and len(coll_name) != 0):
                            CollectionManagement.create_Container(client, db_name, coll_name)
                        else:
                             print("Invalid database or collection name provided")
                    elif choice == 8:
                        print("Menu 8 has been selected")
                        db_name = str(input("Please provide the database where documents will be created: "))
                        coll_name = str(input("Please provide a collection name where documents will be created: "))
                        if (len(db_name) != 0 and len(coll_name) != 0):
                            DocumentManagement.CreateDocuments(client, db_name, coll_name)
                        else:
                             print("Invalid database or collection name provided")                            
                    elif choice == 9:
                        print("Menu 9 has been selected")
                        db_name = str(input("Please provide the database name: "))
                        coll_name = str(input("Please provide a collection name: "))
                        if (len(db_name) != 0 and len(coll_name) != 0):
                            DocumentManagement.ReadDocument(client, db_name, coll_name, 'SalesOrder1')
                        else:
                             print("Invalid database or collection name provided")
                    elif choice == 10:
                        print("Menu 10 has been selected")
                        db_name = str(input("Please provide the database name: "))
                        coll_name = str(input("Please provide a collection name: "))
                        if (len(db_name) != 0 and len(coll_name) != 0):
                            DocumentManagement.ReadDocuments(client, db_name, coll_name)

                    elif choice == 11:
                        print("Menu 11 has been selected")
                        db_name = str(input("Please provide a database name to be deleted: "))
                        DatabaseManagement.delete_database(client, DATABASE_ID)
                        
                    elif choice == 12:                       
                        print("Menu 12 has been selected")
                        #  delete collection by id
                        db_name = str(input("Please provide the database name where the collection is located: "))
                        coll_name = str(input("Please provide a collection name to be deleted: "))
                        if (len(coll_name) != 0 and len(db_name) != 0):
                                CollectionManagement.delete_Container(client, db_name, coll_name)
                        else:
                                print("Invalid database or collection name provided!")

                         
                    elif choice == 13:
                        print("Menu 13 has been selected, exiting...")
                        ## You can add your code or functions here
                        loop = False # This will make the while loop to end as not value of loop is set to False
                        
                    else:
                        # Any integer inputs other than values 1-5 we print an error message
                        input("Wrong option selection. Enter any key to try again..")
       
            except errors.HTTPFailure as e:
                print('\nrun_sample has caught an error. {0}'.format(e))
            finally:
                print("\nrun_sample done")
   
if __name__ == '__main__':
        try:
            run_sample()

        except Exception as e:
                print("Top level Error: args:{0}, message:{1}".format(e.args,e))