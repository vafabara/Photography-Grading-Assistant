import customtkinter as ctk
from PIL import ImageTk

from .histogram_panel import HistogramPanel
from .widgets import show_note_dialog


class ImageViewer:

    def __init__(self, parent, on_drop=None, on_note_save=None):

        self.on_note_save = on_note_save
        self.image_record = None

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
        self.create_note_bar()

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

    def create_note_bar(self):
        """
        Replaces the old Recent Files area in the preview (new
        feature: Photo Note). Clicking it opens a small dialog to
        add/edit a note for whichever photo is currently on screen.
        The note itself is persisted by App into that photo's
        core.class_model.ClassPhotoEntry -- this widget only renders
        it and reports edits back via on_note_save.
        """

        self.note_bar = ctk.CTkButton(
            self.frame,
            text="📝  Add Note...",
            anchor="w",
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            border_width=1,
            text_color="#7CFFB2",
            command=self.open_note_dialog
        )

        self.note_bar.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=(0, 12)
        )

    def open_note_dialog(self):

        if self.image_record is None:
            return

        current_note = self.image_record.note or ""

        def handle_save(new_note):

            self.image_record.note = new_note
            self.refresh_note_bar()

            if self.on_note_save:
                self.on_note_save(self.image_record, new_note)

        show_note_dialog(
            self.frame,
            current_note,
            on_save=handle_save
        )

    def refresh_note_bar(self):

        if self.image_record and self.image_record.note:
            preview = self.image_record.note.strip().splitlines()[0][:40]
            self.note_bar.configure(text=f"📝  {preview}")
        else:
            self.note_bar.configure(text="📝  Add Note...")

    def update(self, image, image_record=None):

        self.image_record = image_record

        self.current_image = image.copy()

        image = image.copy()
        image.thumbnail((500, 500))

        self.image_tk = ImageTk.PhotoImage(image)

        self.preview_label.configure(
            image=self.image_tk,
            text=""
        )

        self.histogram.update(self.current_image)
        self.refresh_note_bar()