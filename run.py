from app import createApp, database
from flask_cors import CORS

app = createApp()
CORS(app,
     supports_credentials=True,
     origins=lambda origin: origin and origin.endswith("vercel.app"))
with app.app_context():
    database.create_all()

if __name__ == "__main__":
    app.run(debug=True)