class ViddlerAPIException(EnvironmentError):
    def __init__(self, code, description="", details=""):
        self.code = code
        self.description = description
        self.details = details
        message = "Viddler API Error %s: %s. Details: %s" % (self.code, self.description, self.details)

        super(ViddlerAPIException, self).__init__(message)
