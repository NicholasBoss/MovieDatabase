import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def initialize_firestore():
    """
    Create database connection
    """

    # Setup Google Cloud Key - The json file is obtained by going to 
    # Project Settings, Service Accounts, Create Service Account, and then
    # Generate New Private Key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "movies-99506-firebase-adminsdk-j3wrc-03d92febbf.json"

    # Use the application default credentials.  The projectID is obtianed 
    # by going to Project Settings and then General.
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'movies-99506',
    })

    # Get reference to database
    db = firestore.client()
    return db

def add_new_item(db):
    '''
    Prompt the user for a new item to add to the movie database.  The
    item name must be unique (firestore document id).  
    '''

    title = input("Movie Title: ")
    year = int(input("Year Released: "))
    rating = input("Rating ('G','PG' or 'PG-13'): ") 
    studio = input("Movie Studio: ")
    media_type = input("Media Type: ")
    actors = input("Actors (separate each actor with a comma): ")
    genres = input("Genres (separate each genre with a comma): ")
    special_features = input("Special Features (separate each feature with a comma): ")
    qty = int(input("Quantity of movies to add: "))
    popular = input("Is this movie popular? (y/n): ").lower() == "y"
    

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("movies").document(title).get()
    if result.exists:
        print("Item already exists.")
        return

    # Build a dictionary to hold the contents of the firestore document.
    data = {"year" : year, 
            "rating" : rating,
            "studio" : studio,
            "media_type" : media_type,
            "actors" : [actors],
            "genres" : [genres],
            "special_features" : [special_features],
            "qty" : qty,
            "popular" : popular}
    db.collection("movies").document(title).set(data) 

    # Save this in the log collection in Firestore       
    log_transaction(db, f"Added {title} with initial quantity {qty}")

def add_inventory(db):
    '''
    Prompt the user to add quantity to an already existing item in the
    inventory database.  
    '''

    title = input("Movie Title: ")
    add_qty = int(input("Add Quantity: "))

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("movies").document(title).get()
    if not result.exists:
        print("Invalid Movie Name")
        return

    # Convert data read from the firestore document to a dictionary
    data = result.to_dict()

    # Update the dictionary with the new quanity and then save the 
    # updated dictionary to Firestore.
    data["qty"] += add_qty
    db.collection("movies").document(title).set(data)

    # Save this in the log collection in Firestore
    log_transaction(db, f"Added {add_qty} {title}")

def use_inventory(db):
    '''
    Prompt the user to use quantity from an already existing item in the
    inventory database.  An error will be given if the requested amount
    exceeds the quanity in the database.
    '''

    title = input("Movie Title: ")
    use_qty = int(input("Use Quantity: "))

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("movies").document(title).get()
    if not result.exists:
        print("Invalid Movie Title")
        return

    # Convert data read from the firestore document to a dictionary
    data = result.to_dict()

    # Check for sufficient quantity.
    if use_qty > data["qty"]:
        print(f"Not enough inventory. Only {data['qty']} left.")
        return

    # Update the dictionary with the new quanity and then save the 
    # updated dictionary to Firestore.
    data["qty"] -= use_qty
    db.collection("movies").document(title).set(data)

    # Save this in the log collection in Firestore
    log_transaction(db, f"Used {use_qty} {title}")

def search_inventory(db):
    '''
    Search the database in multiple ways.
    '''

    print("Select Query")
    print("1) Show All Inventory")        
    print("2) Show Unstocked Inventory")
    choice = input("> ")
    print()

    # Build and execute the query based on the request made
    if choice == "1":
        results = db.collection("movies").get()
    elif choice == "2":
        results = db.collection("movies").where("qty","==",0).get()
    else:
        print("Invalid Selection")
        return
    
    # Display all the results from any of the queries
    print("")
    print("Search Results")
    print(f"{'Title':<20}  {'Year':<10}  {'Rating':<10}  {'Studio':<10}  {'Media Type':<10} {'qty':<10}")
    for result in results:
        item = result.to_dict()
        print(f"{result.id:<20} {item['year']:<10}  {item['rating']:<10}  {item['studio']:<10}  {item['media_type']:<10} {item['qty']:<10}")
    print()    

def log_transaction(db, message):
    '''
    Save a message with current timestamp to the log collection in the
    Firestore database.
    '''
    data = {"message" : message, "timestamp" : firestore.SERVER_TIMESTAMP}
    db.collection("log").add(data)    

def notify_stock_alert(results, changes, read_time):
    '''
    If the query of out of stock items changes, then display the changes.
    ADDED = New out of stock item added to the list since registration
    MODIFIED = An out of stock item was modified but still out of stock
    REMOVED = An out of stock item is no longer out of stock
    '''

    for change in changes:
        if change.type.name == "ADDED": 
            print()
            print(f"OUT OF STOCK ALERT!! ORDER MORE: {change.document.id}")
            print()
        elif change.type.name == "REMOVED":
            print()
            print(f"ITEM HAS BEEN RE-STOCKED!! READY TO USE: {change.document.id}")
            print()
    
def register_out_of_stock(db):
    '''
    Request a query to be monitored.  If the query changes, then the
    notify_stock_alert will be called.
    '''
    db.collection("movies").where("qty","==",0).on_snapshot(notify_stock_alert)

def main():
    db = initialize_firestore()
    register_out_of_stock(db)
    choice = None
    while choice != "0":
        print()
        print("0) Exit")
        print("1) Add New Movie")
        print("2) Add Quantity")
        print("3) Use Quantity")
        print("4) Search Inventory")
        choice = input(f"> ")
        print()
        if choice == "1":
            add_new_item(db)
        elif choice == "2":
            add_inventory(db)
        elif choice == "3":
            use_inventory(db)
        elif choice == "4":
            search_inventory(db)                        

if __name__ == "__main__":
    main()