# Overview

XabarBot.UZ is a Flask-based AI-powered web application featuring intelligent chat functionality using Google's Gemini AI. The application provides user authentication, knowledge base management for context-aware responses, and a clean web interface. The system allows users to upload documents which are then used to provide more contextual AI responses during chat sessions. The application is fully configured for the Replit environment with proper database integration and deployment settings.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Primary web framework with Blueprint-based modular architecture
- **Template Engine**: Jinja2 templating system with responsive web interface in Uzbek language
- **Configuration**: Production-ready Flask application with proper environment variable handling and security features

## Application Structure
- **Modular Design**: Blueprint-based architecture with separate modules for authentication, chat, and knowledge base functionality
- **MVC Pattern**: Models (`models/`), Views (`templates/`), and Controllers (`routes/`) properly separated
- **Production-Ready**: Configured for both development and production deployment with gunicorn

## Database Integration
- **PostgreSQL**: Full PostgreSQL integration with psycopg2-binary driver
- **Models**: User management and knowledge base storage with proper relationships
- **Environment**: Uses DATABASE_URL for seamless database connectivity

## AI Integration
- **Google Gemini**: Integrated AI chat functionality using Google's Generative AI API
- **Context-Aware**: Knowledge base integration for contextual AI responses
- **API Management**: Proper API key handling through environment variables

# External Dependencies

## Python Packages
- **Flask 3.0.3**: Web framework with Flask-WTF for form handling
- **PostgreSQL**: psycopg2-binary for database connectivity
- **AI Integration**: google-generativeai for AI chat functionality
- **Security**: bcrypt for password hashing
- **File Processing**: PyPDF2, python-docx, pandas for knowledge base file parsing
- **Production**: gunicorn for production WSGI server deployment

## Runtime Environment
- **Python 3.11**: Full Python runtime with all required dependencies
- **Database**: PostgreSQL database with automatic table creation
- **Production Server**: Gunicorn WSGI server for production deployment

## Environment Variables
- **GEMINI_API_KEY**: Google Gemini API key for AI functionality
- **DATABASE_URL**: PostgreSQL connection string
- **SESSION_SECRET**: Flask session security (optional, auto-generated if not set)
- **PORT**: Application port (defaults to 5000 for development)

# Recent Changes

## 2025-09-14: Complete XabarBot.UZ Platform Implementation
- **Core Platform Completed**: Built comprehensive SaaS AI chatbot platform
- **Database Schema**: Updated PostgreSQL with SQLAlchemy models for users, knowledge base, contact logs, and Telegram bots
- **Authentication System**: Flask-Login with trial periods, plan management, and phone validation
- **Template System**: Production-ready Bootstrap 5 responsive templates with CSRF protection
- **AI Integration**: Google Gemini AI with context-aware responses using knowledge base content
- **3-Channel Contact System**: Integrated webchat widget, phone call requests, and Telegram bot functionality
- **Knowledge Base**: File upload system supporting PDF, DOCX, CSV, TXT with automatic parsing
- **Admin Panel**: User management dashboard with plan and trial monitoring
- **Security**: CSRF protection for all forms and AJAX endpoints, secure session management
- **Platform Architecture**: Modular Flask blueprint structure ready for production deployment