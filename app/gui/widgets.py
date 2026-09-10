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


def show_confirm(parent, message, on_yes):
    """
    Modal Yes/No confirmation dialog (new feature: Delete Class /
    Delete Student confirmations). Calls `on_yes()` only if the user
    picks Yes -- picking No or closing the dialog does nothing.
    """

    confirm_window = ctk.CTkToplevel(parent)

    confirm_window.title("Confirm")
    confirm_window.geometry("400x180")
    confirm_window.resizable(False, False)
    confirm_window.grab_set()

    label = ctk.CTkLabel(
        confirm_window,
        text=message,
        font=ctk.CTkFont(size=15),
        wraplength=340,
        justify="center"
    )

    label.pack(pady=(35, 20))

    def handle_yes():
        confirm_window.destroy()
        on_yes()

    button_row = ctk.CTkFrame(
        confirm_window,
        fg_color="transparent"
    )

    button_row.pack()

    ctk.CTkButton(
        button_row,
        text="Yes",
        width=100,
        fg_color="#1F8F4C",
        hover_color="#27AE60",
        command=handle_yes
    ).pack(
        side="left",
        padx=10
    )

    ctk.CTkButton(
        button_row,
        text="No",
        width=100,
        fg_color="transparent",
        hover_color="#3a1f1f",
        border_color="#FF6B6B",
        border_width=1,
        text_color="#FF6B6B",
        command=confirm_window.destroy
    ).pack(
        side="left",
        padx=10
    )