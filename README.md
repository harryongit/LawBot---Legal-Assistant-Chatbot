# LawBot - Legal Assistant Chatbot

A Django-based legal assistant chatbot that provides general legal information using OpenAI's GPT API.

## Features

- Interactive chat interface
- Legal information assistance
- Conversation history storage
- Modern, responsive UI
- Docker support for easy deployment

## Quick Start with Docker

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd lawbot
```

### 2. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

### 4. Access the Application

Open your browser and go to: `http://localhost:8000`

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

You need to set up your OpenAI API key as an environment variable:

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Copy the key and set it as the environment variable above

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

Open your browser and go to: `http://127.0.0.1:8000/`

## Docker Commands

### Build and Run with Docker

```bash
# Build the image
docker build -t lawbot .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here lawbot
```

### Using Docker Compose

```bash
# Start the application
docker-compose up

# Start in background
docker-compose up -d

# Stop the application
docker-compose down

# Rebuild and start
docker-compose up --build
```

## Troubleshooting

### "Error contacting GPT API" Issues

1. **Check API Key**: Ensure your `OPENAI_API_KEY` environment variable is set correctly
2. **Verify API Key**: Make sure your API key is valid and has sufficient credits
3. **Network Issues**: Check your internet connection
4. **Rate Limits**: If you hit rate limits, wait a moment and try again

### Common Error Messages

- **"OpenAI API key is not configured"**: Set the `OPENAI_API_KEY` environment variable
- **"Invalid API key"**: Check that your API key is correct
- **"Rate limit exceeded"**: Wait a moment before trying again

### Docker Issues

- **Port already in use**: Change the port in `docker-compose.yml` or stop other services using port 8000
- **Permission denied**: Make sure Docker has proper permissions
- **Build fails**: Check that all files are present and Dockerfile is correct

## Project Structure

```
lawbot/
├── chatbot/          # Main chatbot application
│   ├── models.py     # Database models
│   ├── views.py      # Chat view logic
│   └── urls.py       # URL routing
├── templates/        # HTML templates
│   ├── base.html     # Base template
│   └── index.html    # Chat interface
├── lawbot/           # Django project settings
│   └── settings.py   # Project configuration
├── Dockerfile        # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt  # Python dependencies
├── .dockerignore     # Docker ignore file
├── env.example       # Environment variables example
└── manage.py         # Django management script
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `DEBUG` | Django debug mode | No (default: True) |
| `SECRET_KEY` | Django secret key | No (auto-generated) |

## Legal Disclaimer

This chatbot provides general legal information only. It is not a substitute for professional legal advice. Always consult with a qualified attorney for specific legal matters.
