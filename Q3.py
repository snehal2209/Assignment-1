# ●The program should read a configuration file (you can provide them with a sample configuration file).
# ●It should extract specific key-value pairs from the configuration file.
# ●The program should store the extracted information in a data structure (e.g., dictionary or list).
# ●It should handle errors gracefully in case the configuration file is not found or cannot be read.
# ●Finally save the output file data as JSON data in the database.
# ●Create a GET request to fetch this information.
# Sample Configuration file: 
# [Database]
# host = localhost
# port = 3306
# username = admin
# password = secret
# [Server]
# address = 192.168.0.1
# port = 8080
# Sample Output: 
# Configuration File Parser Results:
# Database:
# - host: localhost
# - port: 3306
# - username: admin
# - password: secret
# Server:
# - address: 192.168.0.1
# - port: 8080 

import configparser
import json
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

def parse_config(filepath):
    """Parses the configuration file and returns a dictionary with the data."""
    config = configparser.ConfigParser()
    try:
        config.read(filepath)
        config_data = {section: dict(config.items(section)) for section in config.sections()}
        return config_data
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return None

def save_to_mongodb(data):
    """Saves the configuration data as JSON to MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/")  
        db = client["Task"]  
        collection = db["Q3"]

        # Converting to JSON string 
        json_data = json.dumps(data)
        
        # Insertting the JSON string as a document.
        result = collection.insert_one({"config_json": json_data})

        print(f"Data saved to MongoDB successfully.  Inserted ID: {result.inserted_id}")
        client.close()
        return True
    except Exception as e:
        print(f"MongoDB error: {e}")
        return False


@app.route('/config', methods=['GET'])
def get_config():
    """API endpoint to fetch the configuration data from MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
        db = client["Task"]
        collection = db["Q3"]

        # Find the latest document (you might want a better way to order/version)
        latest_config = collection.find_one({}, sort=[("_id", -1)])  # Sort by _id descending

        client.close()

        if latest_config:
            config_data = json.loads(latest_config["config_json"])
            return jsonify(config_data), 200
        else:
            return jsonify({"message": "No configuration data found."}), 404

    except Exception as e:
        print(f"MongoDB error: {e}")
        return jsonify({"message": "Error fetching data from MongoDB."}), 500


if __name__ == '__main__':
    config_file = "config.ini"
    config_data = parse_config(config_file)

    if config_data:
        # ... (print config data)

        if save_to_mongodb(config_data):
            app.run(debug=True)
    else:
        print("Failed to parse configuration. Exiting.")


# Key Changes for MongoDB:
#  * pymongo Library:  Uses the pymongo library for MongoDB interaction.  Install it: pip install pymongo
#  * Connection String: Replace "mongodb://your_mongodb_connection_string" with your actual MongoDB connection string.  This string typically includes the username, password, host, and port of your MongoDB server.  Example:  "mongodb://username:password@cluster0-shard-00-00.example.mongodb.net:27017,cluster0-shard-00-01.example.mongodb.net:27017,cluster0-shard-00-02.example.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
#  * Database and Collection:  Replace "your_db_name" and "config_data" with the name of your MongoDB database and collection.
#  * save_to_mongodb():  This function now uses pymongo to connect to MongoDB and insert the configuration data as a JSON string into a document.
#  * get_config():  This function now retrieves the latest configuration data from MongoDB using collection.find_one({}, sort=[("_id", -1)]). This sorts the documents by the _id field (which MongoDB automatically adds) in descending order to get the most recent one.  You might want to implement a better versioning or timestamping mechanism if you need to manage multiple versions of your configuration.
#  * Error Handling:  Uses try...except blocks to catch potential MongoDB errors.
#  * JSON Handling:  The code still converts the dictionary to a JSON string before saving it to MongoDB. While MongoDB can handle dictionaries directly, serializing to JSON can be useful if you want to ensure a consistent format or if you're working with tools that expect JSON data. You could insert the data dictionary directly into the collection without serializing it.
# How to Run (with MongoDB):
#  * Install Libraries: pip install configparser Flask pymongo
#  * Create config.ini: (same as before)
#  * Start MongoDB: Make sure your MongoDB server is running.
#  * Run the script: python your_script_name.py
#  * Access the API: (same as before)
# This version uses MongoDB as the database to store and retrieve the configuration data.  Remember to configure the connection string and database/collection names correctly.


