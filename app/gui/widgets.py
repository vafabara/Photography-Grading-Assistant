import customtkinter as ctk


def create_info_label(parent, text):

    label = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=14),
        anchor="w"
    )

    label.pack(
        fill="x",
        padx=20,
        pady=5
    )

    return label


def show_error(parent, message):

    error_window = ctk.CTkToplevel(parent)

    error_window.title("Error")
    error_window.geometry("400x180")
    error_window.resizable(False, False)

    label = ctk.CTkLabel(
        error_window,
        text=message,
        font=ctk.CTkFont(size=15),
        wraplength=340
    )

    label.pack(pady=(35, 20))

    button = ctk.CTkButton(
        error_window,
        text="OK",
        width=100,
        command=error_window.destroy
    )

    button.pack()