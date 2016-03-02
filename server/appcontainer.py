from app import create_app
import config
import stacksampler


app = create_app()
profile_server_thread = stacksampler.run_profiler()

if __name__ == '__main__':
    app.run(port=5000, debug=config.DEBUG, host='0.0.0.0')