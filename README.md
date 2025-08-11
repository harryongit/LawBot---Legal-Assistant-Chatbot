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
git clone https://github.com/harryongit/LawBot---Legal-Assistant-Chatbot.git
cd lawbot
```

### 2. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env .env
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

## Legal Disclaimer

This chatbot provides general legal information only. It is not a substitute for professional legal advice. Always consult with a qualified attorney for specific legal matters.

<img width="801" height="797" alt="{4B7C4CB0-B81A-4116-84BA-DB2CC2ED83D0}" src="https://github.com/user-attachments/assets/fa1dc758-c030-4125-a4ff-082666f774d7" />

<img width="1197" height="817" alt="image" src="https://github.com/user-attachments/assets/bd7dad7c-cbf8-45f2-bb1c-d2e5ff639c95" />

<img width="1778" height="640" alt="image" src="https://github.com/user-attachments/assets/23c5f547-2071-4134-aeab-a44489bde901" />

<img width="1888" height="913" alt="image" src="https://github.com/user-attachments/assets/323d0d1f-07f5-4991-a2ef-893c07649d1b" />

<img width="1915" height="911" alt="{797111F8-6326-4B03-A36C-18F9AE240326}" src="https://github.com/user-attachments/assets/fe201241-d85b-40bd-9d14-1e4ba626f3ec" />

