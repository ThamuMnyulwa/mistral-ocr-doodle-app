#!/bin/bash

echo "🚀 Preparing for Streamlit Cloud deployment..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    echo "__pycache__/" > .gitignore
    echo "*.pyc" >> .gitignore
    echo ".env" >> .gitignore
    echo ".streamlit/secrets.toml" >> .gitignore
fi

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "Please create requirements.txt with your project dependencies."
    exit 1
fi

# Add all files
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Prepare for Streamlit Cloud deployment"

echo """
✨ Setup complete! To deploy to Streamlit Cloud:

1. Create a repository on GitHub and push your code:
   git remote add origin <your-github-repo-url>
   git push -u origin main

2. Visit https://share.streamlit.io/ and:
   - Sign in with GitHub
   - Click 'New app'
   - Select your repository
   - Select the main branch
   - Set the path to 'app/streamlit_app.py'
   - Click 'Deploy'

3. Don't forget to add your MISTRAL_API_KEY in the Streamlit Cloud secrets:
   - Go to your app settings
   - Find 'Secrets'
   - Add your API key as:
     MISTRAL_API_KEY='your-api-key'

🎉 Your app will be live at https://share.streamlit.io/your-username/your-repo-name
""" 