# Import the 'create_app' function and the 'socketio' object from the 'website' package.
from website import create_app, socketio

# Call the 'create_app' function to create a Flask application instance.
app = create_app()

# This is the main entry point of the program.
if __name__ == '__main__':
    # Run the Socket.IO web server.
    # The 'debug' parameter is set to 'True', enabling debug mode.
    # The 'host' parameter is set to '0.0.0.0', meaning the server is publicly available.
    # The 'port' parameter is set to '5000', meaning the server listens on port 5000.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
