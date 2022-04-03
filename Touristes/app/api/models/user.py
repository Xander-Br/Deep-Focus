class User:
    def __init__(self,id, name, video):
        self.id = id
        self.name = name
        self.video = video
        self.score = []

    def asDict(self):
        score_average = None
        if(sum(self.score) == 0):
            pass
        else:
            score_average = sum(self.score)/len(self.score)
        asDict = {
            "id": self.id,
            "name": self.name,
            "score_average": score_average
        }
        return asDict
    def getAverage(self):
        score_average = None
        if (sum(self.score) == 0):
            return 0
        else:
            return sum(self.score) / len(self.score)