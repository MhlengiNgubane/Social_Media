# Social Media App

## Overview

This is a Django-based social media application designed for users to connect, share posts, follow others, and engage in chats. The app includes user authentication, profile management, notifications, and real-time chat functionality.

## Features

### Users

- **User Registration**: Users can sign up with a unique username and email address.
- **User Authentication**: Secure login and logout functionalities.
- **Profile Management**: Users can update their profile information, including a bio, profile picture, and cover photo.
- **Follow/Unfollow System**: Users can follow or unfollow other users. The followers list is dynamically updated.

### Posts

- **Create Posts**: Users can create text and media posts.
- **View Posts**: Users can view posts from the people they follow.
- **Like and Comment**: Users can like and comment on posts to engage with content.

### Notifications

- **Real-time Notifications**: Users receive notifications for various activities, including when someone follows them or interacts with their posts.
- **Notification Management**: Users can view a list of their notifications.

### Chats

- **Real-time Chat**: Users can send and receive messages in real time.
- **Chat History**: Users can view their previous chat messages.
- **Direct Messaging**: Users can initiate chats with other users.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Django 3.0 or higher
- Django REST Framework
- Channels (for real-time chat)
- PostgreSQL or another database supported by Django

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/MhlengiNgubane/Social_Media.git
   cd social-media-app
