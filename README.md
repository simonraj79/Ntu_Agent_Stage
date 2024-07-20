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
- Marked.js (Markdown Rendering)
- DOMPurify (HTML Sanitization)

Here is the analysis of the NTUAgent app based on the content of the files provided:

### Main Logic of the NTUAgent App

#### Initialization and Configuration
- **`__init__.py`**: This file initializes the Flask app, sets up the database, registers blueprints, and configures middleware.
- **`config.py`**: Contains configuration settings for the app, such as database URI and secret keys.
- **`run.py`**: The entry point of the application. It runs the Flask app.

#### Database Management
- **`db.py`**: Manages the database connection and ORM setup using SQLAlchemy.
- **`update_cat.py`**: A script for updating certain database tables, likely used for maintenance or data migration purposes.

#### Models
- **`agent.py`**: Defines the `Agent` model, which represents the chatbot agents.
- **`conversation.py`**: Defines the `Conversation` model, which represents the conversations between users and agents.
- **`user.py`**: Defines the `User` model, which represents the users of the platform.

#### Forms
- **`forms.py`**: Defines the forms used in the application with WTForms, including user registration, login, and agent creation forms.

#### Navigation Configuration
- **`nav_config.py`**: Contains the configuration for the application's navigation bar, including the links and their visibility based on user authentication.

#### Routes
- **`agents.py`**: Handles routes related to chatbot agents, such as creating, editing, viewing, and chatting with agents.
- **`auth.py`**: Manages user authentication routes, including login, logout, and registration.
- **`main.py`**: Contains the main routes and views for the application, such as the home page and dashboards.

#### Static Files
- **CSS Files**: Define the styles for various pages and components in the application.
  - `agent_directory.css`
  - `base.css`
  - `chat.css`
  - `conversation_history.css`
  - `create_agent.css`
  - `edit_agent.css`
  - `faculty_dashboard.css`
  - `login.css`
  - `register.css`
  - `student_dashboard.css`
  - `view_conversation.css`

- **JavaScript Files**:
  - `chat.js`: Manages the chat functionality, including sending and receiving messages.
  - `insights.js`: Adds functionality to generate insights on button click.
  - `main.js`: Sets up CSRF protection for all AJAX requests and handles global JavaScript functionality.

#### Templates
- **HTML Templates**: Define the structure and layout of the web pages.
  - `agent_directory.html`: Displays the directory of available agents.
  - `base.html`: The base template extended by other templates, includes overall layout and navigation.
  - `chat.html`: The chat interface where users can interact with the chatbot.
  - `conversation_history.html`: Displays the conversation history and allows filtering by agent and date.
  - `create_agent.html`: The form for creating a new chatbot agent.
  - `edit_agent.html`: The form for editing an existing chatbot agent.
  - `faculty_dashboard.html`: The dashboard for faculty members, providing an overview of their agents and recent conversations.
  - `home.html`: The home page welcoming users to the platform.
  - `login.html`: The login page for user authentication.
  - `register.html`: The registration page for new users.
  - `student_dashboard.html`: The dashboard for students, displaying available chatbots and recent chats.
  - `view_conversation.html`: Shows the details of a specific conversation along with insights.

### Key Functionalities
1. **User Authentication**: Users can register, log in, and log out. Different roles (e.g., student, faculty) might have different access levels.
2. **Chat Management**: Users can interact with chatbot agents via a chat interface. Messages are displayed with a distinction between user and AI responses.
3. **Agent Management**: Users (especially faculty) can create, edit, and manage chatbot agents. Agents can be categorized and have different access levels (public, private, etc.).
4. **Conversation History and Insights**: Users can view the history of their conversations with agents and generate insights (e.g., topics, sentiment analysis).
5. **Dashboards**: Separate dashboards for faculty and students to manage their interactions with the chatbots.
6. **Navigation**: Dynamic navigation bar based on user authentication status and roles.
7. **Security**: Implements CSRF protection for all AJAX requests to prevent cross-site request forgery.

### Typical Workflow
1. **Initialization**: The application initializes the Flask app and sets up database connections.
2. **User Interaction**: Users interact with the application through various routes and views, such as home, login, registration, and dashboards.
3. **Chat Interaction**: Users send messages through a chat interface, which are processed and responded to by the chatbot agents.
4. **Insight Generation**: Users can generate insights from the chat data, which are displayed on the interface.
5. **Database Operations**: All interactions and data are stored and managed through SQLAlchemy.
6. **Agent Management**: Users can create, view, edit, and delete chatbot agents.

This comprehensive overview captures the main logic and functionalities of the NTUAgent app based on the provided files. If you need more detailed information on specific parts, feel free to ask!
## Application Logic

The NTUAgent application follows these main steps:

1. Faculty members register and log in to the platform.
2. Faculty members create AI agents by providing a name, description, system prompt, category, and other settings.
3. Users interact with the agents through a chat interface.
4. User messages are sent to the OpenAI API, along with the conversation history and agent's system prompt, to generate agent responses.
5. The chat history and agent details are stored in the database.
6. Faculty members can view and manage their created agents, including editing and deleting them.
7. Faculty members can view conversation history for their agents and generate insights.
8. Students can browse and interact with public agents.
9. The application handles token count limits and streams responses from the OpenAI API for a seamless user experience.

## Contributing

Contributions to the NTUAgent project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is copyrighted under NTU. For more information, please refer to the licensing details provided within the project documentation or contact the project administrators.
