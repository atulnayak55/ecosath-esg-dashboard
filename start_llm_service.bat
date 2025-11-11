@echo off
cd /d "d:\NOI hackathon\Infolabs"
set GCP_PROJECT_ID=your-gcp-project-id
echo Starting LLM Service on port 8005...
python api/llm_service.py
pause
