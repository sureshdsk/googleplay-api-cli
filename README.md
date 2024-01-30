# googleplay-api-cli
Example for googleplay-api 

```
# install dependencies 
pip install -r requirements.txt

# Login via environment variable
GPLAY_EMAIL=test@gmail.com GPLAY_PASSWORD=testtesttest python main.py login

# Login directly
python main.py login test@gmail.com testpassword

# Search
python main.py search term 
ex: python main.py search "whatsapp business"

# App Details
python main.py get-app PACKAGE_NAME

# Download APK
python main.py download com.whatsapp.w4b
```