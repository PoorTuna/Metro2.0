import Metro # Import package

if __name__ == "__main__":
	Metro.db.create_all()
	Metro.socketio.run(Metro.app, host='0.0.0.0', port=8080, debug=True)