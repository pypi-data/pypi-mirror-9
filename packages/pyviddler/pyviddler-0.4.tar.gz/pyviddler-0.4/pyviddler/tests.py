from pyviddler import ViddlerAPI

apikey = "15z0p5aul5vbiheho0js"
username = "natgeoed"
password = "Education123"

api = ViddlerAPI(apikey, username, password)
api.users.getProfile()
