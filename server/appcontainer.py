from app import create_app
import config


app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=config.DEBUG, host='0.0.0.0')