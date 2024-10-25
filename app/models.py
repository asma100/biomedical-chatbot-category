from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
import os
import psycopg2
from sqlalchemy import Table, Column, String, ARRAY, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__='User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
# PostgreSQL connection
def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database="chatbot",
        user="postgres",
        password="0"
    )
    return conn

def create_table_for_folder(table_name):
    metadata = MetaData()

    folder_table = Table(
        table_name, metadata,
        Column('subfolder_name', String, primary_key=True),  # Unique constraint on subfolder_name
        Column('file_paths', ARRAY(String))  # Array to store file paths
    )

    # Create the table in the database
    metadata.create_all(db.engine)

def insert_subfolder_data(table_name, subfolder_name, file_paths):
    table = get_table_model(table_name)

    # Upsert logic (Insert if doesn't exist, otherwise update)
    stmt = insert(table).values(
        subfolder_name=subfolder_name,
        file_paths=file_paths
    ).on_conflict_do_update(
        index_elements=['subfolder_name'],  # Update based on this unique constraint
        set_={'file_paths': file_paths}
    )

    # Execute the statement
    db.session.execute(stmt)
    db.session.commit()

# Helper function to get the dynamic model
def get_table_model(table_name):
    metadata = MetaData()
    return Table(
        table_name, metadata,
        Column('subfolder_name', String, primary_key=True),
        Column('file_paths', ARRAY(String)),
        autoload_with=db.engine
    )

import os
from app import db, app
def process_directory(base_folder):
    # Use the application context to interact with db
    with app.app_context():
        # Traverse the base directory
        for folder_name in os.listdir(base_folder):
            folder_path = os.path.join(base_folder, folder_name)

            if os.path.isdir(folder_path):
                # Create a table for each folder
                table_name = folder_name.replace('-', '_').replace(' ', '_')  # Postgres-friendly table names
                create_table_for_folder(table_name)

                # Process subfolders and files
                for subfolder_name in os.listdir(folder_path):
                    subfolder_path = os.path.join(folder_path, subfolder_name)

                    if os.path.isdir(subfolder_path):
                        # Get list of files in the subfolder
                        file_paths = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]

                        # Insert subfolder name and file paths into the table using SQLAlchemy
                        insert_subfolder_data(table_name, subfolder_name, file_paths)

# Base folder containing the main folders
base_folder = r"app\pdfs"

# Now when calling process_directory, it will run within the app context
process_directory(base_folder)

def get_db_session():
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        return session
    
def get_pdf_paths(table_name, subfolder_name):
    with app.app_context():  # Ensure the app context is active
        session = get_db_session()

        # Get the table model dynamically based on the table name
        table = get_table_model(table_name)

        # Query the table for the given subfolder_name
        result = session.query(table).filter_by(subfolder_name=subfolder_name).first()

        # Close the session when done
        session.close()

        # Return the file_paths array if the result is found, otherwise return None
        if result:
            return result.file_paths
        return None


def get_subfolder(table_name):
    with app.app_context():  # Ensure the app context is active
        session = get_db_session()

        # Get the table model dynamically based on the table name
        table = get_table_model(table_name)

        # Query the table to get subfolder_names
        result = session.query(table.c.subfolder_name).all()

        # Close the session when done
        session.close()

        # Extract subfolder names from the result and return them as a list
        subfolder_names = [row[0] for row in result]  # row[0] because result is a list of tuples

        return subfolder_names

