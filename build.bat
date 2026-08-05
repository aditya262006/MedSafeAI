@echo off
echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..
echo Frontend build complete
echo Installing Python dependencies...
pip install -r render_requirements.txt
echo Build complete