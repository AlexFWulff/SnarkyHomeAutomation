class DisplayManager:
    l = None
    def __init__(self, logger):
        self.l = logger

    def wakeword_detected(self):
        pass

    def talking_started(self):
        pass

    def talking_finished(self):
        pass
    
    def transcription_finished(self, text):
        pass

    def got_ai_result(self, result):
        pass

    def ai_result_failed(self, response):
        pass
