from PIL import Image, ImageDraw, ImageFont
import os

def generate_poster(event, club, style=1, save_dir="designed_posters"):
    width, height = 1080, 1350
    os.makedirs(save_dir, exist_ok=True)
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 90)
        desc_font  = ImageFont.truetype("arial.ttf", 50)
        detail_font= ImageFont.truetype("arial.ttf", 45)
    except:
        title_font = desc_font = detail_font = ImageFont.load_default()
    title, desc, venue, date, time = event['name'], event['about'], event['venue'], event['date'], event['time']

    def draw_centered(draw, text, y, font, color):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        x_pos = (width - (text_bbox[2] - text_bbox[0])) // 2
        draw.text((x_pos, y), text, font=font, fill=color)

    def design_one():
        base = Image.new('RGB', (width, height), "#FFD93D")
        draw = ImageDraw.Draw(base)
        draw_centered(draw, title, 160, title_font, "#2D2D2D")
        draw_centered(draw, desc, 300, desc_font, "#2D2D2D")
        y = 470
        for label, val in [("Venue:", venue), ("Date:", date), ("Time:", time)]:
            draw_centered(draw, f"{label} {val}", y, detail_font, "#2D2D2D")
            y += 70
        return base

    def design_two():
        base = Image.new('RGB', (width, height), "#4caf50")
        draw = ImageDraw.Draw(base)
        draw_centered(draw, title, 120, title_font, "#1B5E20")
        draw_centered(draw, desc, 260, desc_font, "#2E7D32")
        y = 430
        for label, val in [("Venue:", venue), ("Date:", date), ("Time:", time)]:
            draw_centered(draw, f"{label} {val}", y, detail_font, "#1B5E20")
            y += 75
        return base

    def design_three():
        base = Image.new('RGB', (width, height), "#2c5364")
        draw = ImageDraw.Draw(base)
        draw_centered(draw, title, 120, title_font, "#00c9a7")
        draw_centered(draw, desc, 250, desc_font, "#00c9a7")
        y = 400
        for label, val in [("Venue:", venue), ("Date:", date), ("Time:", time)]:
            draw_centered(draw, f"{label} {val}", y, detail_font, "#00c9a7")
            y += 80
        return base

    def design_four():
        img = Image.new("RGB", (width, height), "#020024")
        mask = Image.new("L", (width, height))
        mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
        mask.putdata(mask_data)
        top = Image.new("RGB", (width, height), "#7900FF")
        img.paste(top, (0, 0), mask)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.ellipse((100, 100, 500, 500), fill="#FF3CAC44")
        draw.rectangle((600, 400, 1000, 800), fill="#FFFFFF22")
        draw_centered(draw, title, 140, title_font, "white")
        draw_centered(draw, desc, 290, desc_font, "white")
        y = 470
        for label, val in [("Venue:", venue), ("Date:", date), ("Time:", time)]:
            draw_centered(draw, f"{label} {val}", y, detail_font, "white")
            y += 80
        return img

    designs = [design_one, design_two, design_three, design_four]
    fn = designs[style - 1]
    poster = fn()
    filepath = os.path.join(save_dir, f"{title}_poster_style{style}.png")
    poster.save(filepath)
    return filepath
