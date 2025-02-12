from datetime import date


def current_year(request):
    year = date.today().year

    if year > 2024:
        current_year = year
    else:
        current_year = None

    return {"current_year": current_year}
