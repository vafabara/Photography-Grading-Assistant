import customtkinter as ctk
from PIL import ImageTk

from .histogram_panel import HistogramPanel


class ImageViewer:

    def __init__(self, parent, on_drop=None):

        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=12
        )

        self.frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.current_image = None
        self.image_tk = None

        self.create_preview(on_drop)

    def create_preview(self, on_drop):

        self.histogram = HistogramPanel(self.frame)

        self.preview_label = ctk.CTkLabel(
            self.frame,
            text="🖼️\nNo Image Selected\n(or drag & drop one here)",
            text_color="#7CFFB2",
            font=ctk.CTkFont(size=20)
        )

        self.preview_label.pack(
            fill="both",
            expand=True
        )

        if on_drop:
            self.frame.drop_target_register("DND_Files")
            self.frame.dnd_bind(
                "<<Drop>>",
                on_drop
            )

    def update(self, image):

        self.current_image = image.copy()

        image = image.copy()
        image.thumbnail((500, 500))

        self.image_tk = ImageTk.PhotoImage(image)

        self.preview_label.configure(
            image=self.image_tk,
            text=""
        )

        self.histogram.update(self.current_image)