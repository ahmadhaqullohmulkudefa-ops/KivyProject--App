import flet as ft


def main(page: ft.Page):
    page.title = "Five Games"
    page.add(
        ft.Text(
            "Five Games",
            size=30,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text("Flet berhasil berjalan!")
    )


ft.run(main)