from application import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    print("Starting app in dev mode")
    app.run(debug=True, port=3002)
