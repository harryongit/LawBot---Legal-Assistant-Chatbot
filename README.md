# **LawBot – Legal Assistant Chatbot**

A Django-based chatbot that provides **general legal information** using OpenAI’s GPT API.

> ⚖ **Disclaimer**: LawBot is **not** a substitute for professional legal advice. Always consult a qualified attorney for specific legal matters.

---

## **📌 Features**

* 💬 **Interactive Chat Interface** – Real-time question & answer
* 📚 **Legal Information Assistance** – Trained to provide general guidance
* 📝 **Conversation History** – Stores chat history in a database
* 🎨 **Responsive UI** – Modern and clean interface
* 🐳 **Docker Support** – Easy deployment anywhere

---

## **🚀 Quick Start with Docker**

### **1. Clone the Repository**

```bash
git clone https://github.com/harryongit/LawBot---Legal-Assistant-Chatbot.git
cd lawbot
```

### **2. Configure Environment Variables**

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_actual_api_key_here
```

### **3. Run with Docker Compose**

```bash
docker-compose up --build
```

### **4. Access the Application**

Open:

```
http://localhost:8000
```

---

## **⚙ Manual Setup (Without Docker)**

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Configure OpenAI API Key**

**Windows (Command Prompt)**:

```cmd
set OPENAI_API_KEY=your_key_here
```

**Windows (PowerShell)**:

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

**Linux/Mac**:

```bash
export OPENAI_API_KEY=your_key_here
```

### **3. Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **4. Start the Server**

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/
```

---

## **🐳 Docker Commands**

```bash
# Build the image
docker build -t lawbot .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here lawbot
```

**Using Docker Compose**

```bash
docker-compose up -d   # Run in background
docker-compose down    # Stop containers
docker-compose up --build  # Rebuild & run
```

---

## **🛠 Troubleshooting**

### **"Error contacting GPT API"**

1. Check if `OPENAI_API_KEY` is correctly set.
2. Verify the API key is valid and has credits.
3. Ensure internet connectivity.
4. Watch for **rate limits** from OpenAI.

### **Docker Issues**

* **Port in use** → Change port in `docker-compose.yml` or stop other apps using 8000.
* **Permission denied** → Ensure Docker has correct permissions.
* **Build fails** → Check all files & Dockerfile syntax.

---

## **📂 Project Structure**

```
lawbot/
├── chatbot/              # Main chatbot app
│   ├── models.py         # Database models
│   ├── views.py          # Chat logic
│   └── urls.py           # App routes
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── index.html        # Chat interface
├── lawbot/               # Django settings
│   └── settings.py
├── Dockerfile            # Docker config
├── docker-compose.yml    # Docker Compose config
├── requirements.txt      # Python dependencies
├── .dockerignore
├── env.example           # Example env vars
└── manage.py
```

---

## **🖼 Application Screenshots**

<p align="center">
  <img src="https://github.com/user-attachments/assets/fa1dc758-c030-4125-a4ff-082666f774d7" width="45%" />
  <img src="https://github.com/user-attachments/assets/bd7dad7c-cbf8-45f2-bb1c-d2e5ff639c95" width="45%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/23c5f547-2071-4134-aeab-a44489bde901" width="90%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/323d0d1f-07f5-4991-a2ef-893c07649d1b" width="90%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fe201241-d85b-40bd-9d14-1e4ba626f3ec" width="90%" />
</p>

---

## **📜 License**

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---
