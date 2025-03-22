# mistral-ocr-doodle-app
OCR streamlit mistral app. Upload a PDF and get the Markdown.


## Deployment

```bash
chmod +x dev-deploy.sh
```

```bash
./dev-deploy.sh
```
There is a deployment script that helps you prepare your app for Streamlit Cloud deployment. The script has:

1. Created a `.gitignore` file with appropriate exclusions
2. Initialized a git repository (if not already initialized)
3. Committed your changes
4. Provided detailed instructions for deploying to Streamlit Cloud