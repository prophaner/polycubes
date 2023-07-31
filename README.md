Polycube Generator
Polycube Generator is a Python-based tool for generating, encoding, and decoding Polycubes of different sizes. It uses SQLAlchemy to interact with MS SQL Server database, storing and retrieving the polycube data.

Code Structure
The code is divided into three main parts:

1. model.py
This module defines the ORM models and database operations using SQLAlchemy. The main components include:

Database: A class that encapsulates the database operations such as session management, table creation, and data manipulation.
create_polycube_table: A dynamic function that creates a SQLAlchemy model for a polycube table of a given size.
tables: A dictionary where keys are the polycube sizes and the values are the corresponding SQLAlchemy models.
2. worker.py
This module contains the main computational logic of the project. The core functions include:

encoder: This function encodes a 3D numpy array into a binary string for storage in the database.
decoder: This function decodes a binary string from the database back into a 3D numpy array.
trim: This function trims an array to its minimum size by removing the zero padding.
get_neighbors: This function returns the neighbors of a given cell in a 3D array.
get_identities: This function generates all the possible new polycubes by adding a cube to all possible locations.
get_identity: This function normalizes a polycube to its canonical form by performing rotations and comparing the binary representations.
3. controller.py
This module serves as the main entry point for the program. It uses the functionality provided by the model and worker modules to populate the database with new polycubes.

Running the Code
Before running the code, make sure to set your MS SQL Server credentials in the model.py module:

arduino
Copy code
SERVER = 'your_server'
PORT = 'your_port'
DB = 'your_database'
USERNAME = 'your_username'
PASSWORD = 'your_password'
You can run the controller.py script from the command line to start the program:

Copy code
python controller.py
For a simple test run, use the test() function in worker.py.

Dependencies
This project requires Python 3.6 or later, and the following Python libraries:

numpy
sqlalchemy
pymssql
You can install these dependencies using pip:

Copy code
pip install numpy sqlalchemy pymssql
Please note, as the program uses the pymssql library to interface with MS SQL Server, the target environment should have the appropriate system dependencies installed for pymssql. Refer to the pymssql documentation for detailed installation instructions.

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT
