#drop_tables.py
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def reset_database():
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Drop all tables
        cursor.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        """)
        print("All tables dropped successfully.")

        # Create new tables
        cursor.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            display_name VARCHAR(64),
            profile_picture VARCHAR(256),
            bio TEXT,
            is_faculty BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE agent_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(64) UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE agents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(64) NOT NULL,
            description VARCHAR(256),
            system_prompt TEXT,
            creator_id INTEGER REFERENCES users(id) NOT NULL,
            category_id INTEGER REFERENCES agent_categories(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_public BOOLEAN DEFAULT FALSE,
            use_count INTEGER DEFAULT 0
        );

        CREATE TABLE agent_collaborators (
            id SERIAL PRIMARY KEY,
            agent_id INTEGER REFERENCES agents(id) NOT NULL,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            permission_level VARCHAR(20) NOT NULL
        );

        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            agent_id INTEGER REFERENCES agents(id) NOT NULL,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE chat_logs (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id) NOT NULL,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            agent_id INTEGER REFERENCES agents(id) NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE conversation_insights (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id) NOT NULL,
            topics TEXT[],
            sentiment FLOAT,
            summary TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("New tables created successfully.")

    except Exception as error:
        print("Error resetting database:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    reset_database()