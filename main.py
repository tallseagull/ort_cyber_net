from server.ctf_web_server import app

PORT = 8080

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)