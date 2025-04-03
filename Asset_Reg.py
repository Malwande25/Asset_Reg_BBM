import sqlite3
from datetime import datetime

def initialize_database():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    # Create locations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        contact_person TEXT,
        contact_phone TEXT
    )
    ''')
    
    # Create assets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        purchase_date TEXT,
        purchase_price REAL,
        serial_number TEXT,
        category TEXT,
        condition TEXT,
        last_maintenance_date TEXT,
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_location():
    """Add a new church location to the database"""
    print("\nAdd New Church Location")
    print("-----------------------")
    
    name = input("Location Name: ")
    address = input("Address: ")
    contact_person = input("Contact Person: ")
    contact_phone = input("Contact Phone: ")
    
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO locations (name, address, contact_person, contact_phone)
    VALUES (?, ?, ?, ?)
    ''', (name, address, contact_person, contact_phone))
    
    conn.commit()
    conn.close()
    print(f"\nLocation '{name}' added successfully!")

def add_asset():
    """Add a new asset to the database"""
    print("\nAdd New Asset")
    print("-------------")
    
    # Display available locations
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT location_id, name FROM locations')
    locations = cursor.fetchall()
    
    if not locations:
        print("No locations found. Please add a location first.")
        return
    
    print("\nAvailable Locations:")
    for loc in locations:
        print(f"{loc[0]}. {loc[1]}")
    
    try:
        location_id = int(input("\nSelect Location ID: "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Verify location exists
    cursor.execute('SELECT name FROM locations WHERE location_id = ?', (location_id,))
    location_name = cursor.fetchone()
    
    if not location_name:
        print("Invalid location ID.")
        conn.close()
        return
    
    # Get asset details
    name = input("Asset Name: ")
    description = input("Description: ")
    purchase_date = input("Purchase Date (YYYY-MM-DD, leave empty if unknown): ")
    purchase_price = input("Purchase Price (leave empty if unknown): ")
    serial_number = input("Serial Number: ")
    category = input("Category (e.g., Furniture, Equipment, Vehicle): ")
    condition = input("Condition (e.g., New, Good, Fair, Poor): ")
    last_maintenance_date = input("Last Maintenance Date (YYYY-MM-DD, leave empty if none): ")
    
    # Handle empty values
    purchase_date = purchase_date if purchase_date else None
    purchase_price = float(purchase_price) if purchase_price else None
    last_maintenance_date = last_maintenance_date if last_maintenance_date else None
    
    # Insert asset
    cursor.execute('''
    INSERT INTO assets (
        location_id, name, description, purchase_date, purchase_price,
        serial_number, category, condition, last_maintenance_date
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        location_id, name, description, purchase_date, purchase_price,
        serial_number, category, condition, last_maintenance_date
    ))
    
    conn.commit()
    conn.close()
    print(f"\nAsset '{name}' added to {location_name[0]} successfully!")

def view_assets():
    """View all assets with location information"""
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT a.asset_id, l.name as location, a.name, a.description, a.category, a.condition
    FROM assets a
    JOIN locations l ON a.location_id = l.location_id
    ORDER BY l.name, a.name
    ''')
    
    assets = cursor.fetchall()
    
    if not assets:
        print("\nNo assets found in the database.")
        conn.close()
        return
    
    print("\nAsset Register")
    print("--------------")
    current_location = None
    
    for asset in assets:
        if asset[1] != current_location:
            current_location = asset[1]
            print(f"\nLocation: {current_location}")
            print("-" * (10 + len(current_location)))
        
        print(f"ID: {asset[0]}, Name: {asset[2]}")
        print(f"   Description: {asset[3]}")
        print(f"   Category: {asset[4]}, Condition: {asset[5]}\n")
    
    conn.close()

def search_assets():
    """Search for assets by name or description"""
    search_term = input("\nEnter search term: ").strip()
    
    if not search_term:
        print("Please enter a search term.")
        return
    
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT a.asset_id, l.name as location, a.name, a.description, a.category, a.condition
    FROM assets a
    JOIN locations l ON a.location_id = l.location_id
    WHERE a.name LIKE ? OR a.description LIKE ?
    ORDER BY l.name, a.name
    ''', (f'%{search_term}%', f'%{search_term}%'))
    
    assets = cursor.fetchall()
    
    if not assets:
        print("\nNo assets found matching your search.")
        conn.close()
        return
    
    print(f"\nSearch Results for '{search_term}'")
    print("--------------------------------")
    
    for asset in assets:
        print(f"Location: {asset[1]}")
        print(f"ID: {asset[0]}, Name: {asset[2]}")
        print(f"   Description: {asset[3]}")
        print(f"   Category: {asset[4]}, Condition: {asset[5]}\n")
    
    conn.close()

def generate_report():
    """Generate a simple report of assets by location"""
    conn = sqlite3.connect('church_assets.db')
    cursor = conn.cursor()
    
    # Get all locations with asset counts
    cursor.execute('''
    SELECT l.location_id, l.name, COUNT(a.asset_id) as asset_count
    FROM locations l
    LEFT JOIN assets a ON l.location_id = a.location_id
    GROUP BY l.location_id
    ORDER BY l.name
    ''')
    
    locations = cursor.fetchall()
    
    if not locations:
        print("\nNo locations found in the database.")
        conn.close()
        return
    
    print("\nChurch Asset Report")
    print("-------------------")
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_assets = 0
    
    for loc in locations:
        print(f"\nLocation: {loc[1]}")
        print(f"Total Assets: {loc[2]}")
        total_assets += loc[2]
        
        # Get assets for this location
        cursor.execute('''
        SELECT name, category, condition, purchase_date, purchase_price
        FROM assets
        WHERE location_id = ?
        ORDER BY name
        ''', (loc[0],))
        
        assets = cursor.fetchall()
        
        for asset in assets:
            print(f" - {asset[0]} ({asset[1]})")
            print(f"   Condition: {asset[2]}")
            if asset[3]:
                print(f"   Purchased: {asset[3]} for ${asset[4]:.2f}" if asset[4] else f"   Purchased: {asset[3]}")
    
    print(f"\nTotal Assets Across All Locations: {total_assets}")
    conn.close()

def main_menu():
    """Display the main menu and handle user input"""
    while True:
        print("\nChurch Asset Register System")
        print("--------------------------")
        print("1. Add New Location")
        print("2. Add New Asset")
        print("3. View All Assets")
        print("4. Search Assets")
        print("5. Generate Report")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            add_location()
        elif choice == '2':
            add_asset()
        elif choice == '3':
            view_assets()
        elif choice == '4':
            search_assets()
        elif choice == '5':
            generate_report()
        elif choice == '6':
            print("\nExiting the system. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    initialize_database()
    main_menu()
