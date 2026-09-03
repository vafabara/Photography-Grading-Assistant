def get_histogram(image):
    rgb_image = image.convert("RGB")
    r, g, b = rgb_image.split()

    return {
        "r": r.histogram(),
        "g": g.histogram(),
        "b": b.histogram(),
    }