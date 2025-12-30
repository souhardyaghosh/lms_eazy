# 1. Use Python 3.9 on Linux
FROM python:3.9-slim

# 2. Install Google Chrome (The Browser)
RUN apt-get update && apt-get install -y wget gnupg2 unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean

# 3. Set up the app folder
WORKDIR /app
COPY . /app

# 4. Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Start the Website using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]

