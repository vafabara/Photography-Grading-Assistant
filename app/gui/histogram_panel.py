import customtkinter as ctk
from tkinter import Canvas
from ..core.histogram import get_histogram



class HistogramPanel:

    def __init__(self, parent):
        self.canvas = Canvas(
            parent,
            height=110,
            bg="#1a1a1a",
            highlightthickness=0
        )

        self.canvas.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=12
        )

    def update(self, image):

        self.canvas.update_idletasks()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            width, height = 400, 110

        self.canvas.delete("all")

        histogram = get_histogram(image)

        colors = {
            "r": "#FF5C5C",
            "g": "#5CFF9C",
            "b": "#5CA8FF"
        }

        for channel, color in colors.items():

            values = histogram[channel]
            max_value = max(values) or 1

            points = []

            for i, value in enumerate(values):
                x = i * (width / 256)
                y = height - (value / max_value) * (height - 4)

                points.append(x)
                points.append(y)

            if len(points) >= 4:
                self.canvas.create_line(
                    *points,
                    fill=color,
                    width=1,
                    smooth=True
                )