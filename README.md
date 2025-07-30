# Adobe India Hackathon 2025 – Challenge 1B  
## ✨ Persona-Driven Document Intelligence

This project is a submission for **Round 1B** of the **Adobe India Hackathon 2025**. The goal is to build an intelligent engine that extracts and ranks the most relevant sections from a set of tourism-related PDFs based on a user's *persona* and a *specific job-to-be-done*.

---

## 🧠 Problem Overview

You are given 10–13 unstructured travel documents (PDFs). Based on a given **persona** and a **task** :

- Parse each document into semantically meaningful sections
- Rank them based on relevance to the job and persona
- Return a structured JSON with sections and refined summaries


---

## 🚀 Quick Start

### 1. Clone and Set Up
```bash
git clone https://github.com/SaiMaruthiK/challenge_1b.git
cd challenge_1b

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

python main.py \
  --input_dir input \
  --output_dir output \
  --persona 
  --job


##**Docker**
# Build image
docker build -t adobe-hackathon .

# Run container
docker run --rm -v $PWD/input:/app/input -v $PWD/output:/app/output adobe-hackathon \
  --input_dir input \
  --output_dir output \
  --persona "Travel Planner" \
  --job "Plan a trip of 4 days for a group of 10 college friends."

