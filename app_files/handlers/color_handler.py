import random

class ColorHandler:

    @staticmethod
    def randomize_color():
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange']
        return random.choice(colors)
