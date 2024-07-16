# NTUAgent

NTUAgent is a web application that allows faculty members at NTU to create custom AI agents for educational and administrative purposes. The platform provides a user-friendly interface for creating, managing, and interacting with these agents through a chat interface.

## Technologies Used

- Python
- Flask (Web Framework)
- SQLAlchemy (Database ORM)
- Flask-WTF (Form Handling)
- Flask-Login (User Authentication)
- HTML/CSS/JavaScript (Frontend)
- OpenAI API (AI Agent Responses)

## Application Structure

The application follows a modular structure with the following main components:

- `app/`: Contains the main application code
  - `routes/`: Defines the application routes and view functions
  - `models/`: Contains the database model definitions
    - `user.py`: Defines the User model
    - `agent.py`: Defines the AgentCategory, Agent, and AgentCollaborators models
    - `conversation.py`: Defines the Conversation, ChatLog, and ConversationInsights models
  - `utils/`: Contains utility functions
    - `conversation_utils.py`: Defines conversation-related utility functions
  - `forms.py`: Defines the form classes used for user input
  - `static/`: Contains static assets (CSS, JavaScript, images)
  - `templates/`: Contains HTML templates for rendering pages
- `config.py`: Configuration settings for the application
- `run.py`: Entry point to run the application

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/NTUAgent.git
   ```

2. Navigate to the project directory:
   ```
   cd NTUAgent
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - For Windows:
     ```
     venv\Scripts\activate
     ```
   - For macOS and Linux:
     ```
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Set up the database:
   ```
   flask db upgrade
   ```

7. Configure the application:
   - Rename the `.env.example` file to `.env`
   - Update the `.env` file with your OpenAI API key and other necessary configurations

8. Run the application:
   ```
   flask run
   ```

9. Access the application in your web browser at `http://localhost:5000`

## Application Logic

The NTUAgent application follows these main steps:

1. Faculty members register and log in to the platform.
2. Faculty members create AI agents by providing a name, description, and selecting a category.
3. Users interact with the agents through a chat interface.
4. User messages are sent to the OpenAI API to generate agent responses.
5. The chat history and agent details are stored in the database.
6. Faculty members can view and manage their created agents.
7. Students can browse and interact with public agents.

## Contributing

Contributions to the NTUAgent project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is copyrighted under NTU. For more information, please refer to the licensing details provided within the project documentation or contact the project administrators.
