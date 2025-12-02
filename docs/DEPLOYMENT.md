# Deployment Guide

## Prerequisites
- Python 3.10+
- API Keys:
    - Cohere
    - Jina AI
    - Qdrant Cloud

## Local Deployment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multiagent-repo-assistant
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   COHERE_API_KEY=your_key
   QDRANT_API_KEY=your_key
   QDRANT_URL=your_url
   JINA_API_KEY=your_key
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t repo-assistant .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 --env-file .env repo-assistant
   ```

## Production Considerations
- **Security**: Ensure `.env` is not committed to version control.
- **Monitoring**: Check `logs/app.log` for application logs.
- **Scaling**: For heavy loads, consider deploying the vector database and LLM services independently or using enterprise plans.
