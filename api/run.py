import os
from dotenv import load_dotenv

env_file_path = os.path.join(os.getcwd(), ".env")
load_dotenv(env_file_path)

if __name__ == "__main__":
    from app import create_app

    host = os.getenv("API_HOST", "127.0.0.1")
    port = os.environ.get("API_PORT", 5000)
    app = create_app()
    app.run(host=host, port=port, debug=True)
