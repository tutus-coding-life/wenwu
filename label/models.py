class RelicOverview:
    def __init__(self, name, categoryName, culturalRelicNo, dynastyName,centerImage):
        self.name = name
        self.categoryName = categoryName
        self.culturalRelicNo = culturalRelicNo
        self.dynastyName = dynastyName
        self.centerImage = centerImage

    def __str__(self):
        return f"Name: {self.name}, Category: {self.categoryName}, Number: {self.culturalRelicNo}, Dynasty: {self.dynastyName}, Image: {self.centerImage}"

class Tag:
    def __init__(self, Number, MotifAndPattern, ObjectType, FormAndStructure):
        self.Number = Number,
        self.MotifAndPattern = MotifAndPattern 
        self.ObjectType = ObjectType
        self.FormAndStructure = FormAndStructure

        
