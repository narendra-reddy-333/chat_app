# Real-time Chat Application with Django and Channels

This project is a real-time chat application built with Django, Django Channels, and Django REST Framework. It allows
users within an organization to chat with each other in private or group conversations.

## Features

* **User Authentication:** Secure user registration and login.
* **Private Chats:**  One-on-one conversations between users.
* **Group Chats:** Create group chats and invite multiple users.
* **Real-time Messaging:** Instant message delivery using WebSockets and Django Channels.
* **Typing Indicators:** See when other users are typing a message.
* **Unread Message Counts:**  Displays the number of unread messages per conversation.
* **Message Editing (5-minute window):** Edit messages shortly after they are sent.
* **RESTful API:** Access chat functionality through a well-defined API.
* **Scalability:** Built with performance and scalability in mind.

## Technologies Used

* **Django:**  Web framework for backend logic.
* **Django Channels:** Enables WebSocket communication for real-time features.
* **Django REST Framework:**  Build a powerful and flexible API.
* **Redis:**  Message broker for Django Channels.
* **Daphne**: Asynchronous Support for Web server.
* **PostgreSQL (recommended):** Database for storing user data, messages, and other information (you can choose a
  different database if you prefer).

## Project Structure

## Getting Started

### 1. Prerequisites

* Python 3.7+
* PostgreSQL (or your preferred database)
* Redis

### 2. Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/narendra-reddy-333/chat_app
   cd chat_application
2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

5. **Run migrations:**
   ```bash
   python manage.py migrate

6. **Create a superuser (for Django admin):**
   ```bash
   python manage.py createsuperuser

7. **Run the development server using Daphne**
   ```bash
   daphne chat_application.asgi:application -b 0.0.0.0 -p 8000
8. **In another terminal, start the Django Channels worker:**
   ```bash
   python manage.py runworker