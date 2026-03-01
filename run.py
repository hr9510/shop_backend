from app import createApp, database
from flask_cors import CORS

app = createApp()

CORS(
    app,
    origins=["https://shop-tan-ten.vercel.app"],
    supports_credentials=True
)

with app.app_context():
    database.create_all()

if __name__ == "__main__":
    app.run(debug=True)