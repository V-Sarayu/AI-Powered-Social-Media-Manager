from PIL import Image, ImageDraw, ImageFont
import random, os

# INPUT: Customize your event here
event_title = "Startup Fest 2025"
event_description = "Ignite ideas, fuel success!"
event_venue = "XYZ Auditorium"
event_date = "May 3, 2025"
event_time = "9 AM - 6 PM"

width, height = 1080, 1350
output_dir = "designed_posters"
os.makedirs(output_dir, exist_ok=True)

try:
    title_font = ImageFont.truetype("arialbd.ttf", 90)
    desc_font = ImageFont.truetype("arial.ttf", 50)
    detail_font = ImageFont.truetype("arial.ttf", 45)
except:
    title_font = ImageFont.load_default()
    desc_font = ImageFont.load_default()
    detail_font = ImageFont.load_default()

def create_gradient(colors):
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new("L", (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_centered(draw, text, y_position, font, color):
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    x_position = (width - text_width) // 2
    draw.text((x_position, y_position), text, font=font, fill=color)

# Design 1: Tropical Sunset with Smooth Waves (Clean)
def design_one():
    base = create_gradient(("#FF6B6B", "#FFD93D"))
    draw = ImageDraw.Draw(base)

    wave_colors = ["#FF9A76AA", "#FFD93DAA", "#FF6B6BAA"]
    y_levels = [1100, 1170, 1250]
    for y, color in zip(y_levels, wave_colors):
        draw.polygon([
            (0, y), (200, y - 20), (400, y + 20), (600, y - 30),
            (800, y + 10), (1000, y - 15), (width, y), (width, height), (0, height)
        ], fill=color)

    draw_centered(draw, event_title, 130, title_font, "#2D2D2D")
    draw_centered(draw, event_description, 290, desc_font, "#2D2D2D")

    y = 470
    for label, val in [("Venue:", event_venue), ("Date:", event_date), ("Time:", event_time)]:
        draw_centered(draw, f"{label} {val}", y, detail_font, "#2D2D2D")
        y += 80

    return base

# Design 2: Elegant Gradient Clean Green Theme (No circles, no clutter)
def design_two():
    gradient = create_gradient(("#d0f0c0", "#4caf50"))
    draw = ImageDraw.Draw(gradient)
    for i in range(0, height, 60):
        draw.line((0, i, width, i), fill="#c8e6c944", width=1)
    draw_centered(draw, event_title, 120, title_font, "#1B5E20")
    draw_centered(draw, event_description, 260, desc_font, "#2E7D32")

    y = 430
    for label, val in [("Venue:", event_venue), ("Date:", event_date), ("Time:", event_time)]:
        draw_centered(draw, f"{label} {val}", y, detail_font, "#1B5E20")
        y += 75

    return gradient

# Design 3: Futuristic Minimal Gradient with Neon Accents
def design_three():
    img = create_gradient(("#0f2027", "#2c5364"))
    draw = ImageDraw.Draw(img)

    neon = "#00c9a7"
    draw_centered(draw, event_title, 120, title_font, neon)
    draw_centered(draw, event_description, 290, desc_font, neon)

    y = 470
    for label, val in [("Venue:", event_venue), ("Date:", event_date), ("Time:", event_time)]:
        draw_centered(draw, f"{label} {val}", y, detail_font, neon)
        y += 80

    return img

# Design 4: Funky Pop Art Inspired Abstract Geometry
def design_four():
    img = Image.new("RGB", (width, height), "#020024")
    top = Image.new("RGB", (width, height), "#7900FF")
    mask = Image.new("L", (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
    mask.putdata(mask_data)
    img.paste(top, (0, 0), mask)

    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse((100, 100, 500, 500), fill="#FF3CAC44")
    draw.rectangle((600, 400, 1000, 800), fill="#FFFFFF22")
    draw.polygon([(200, 1100), (400, 900), (600, 1100)], fill="#FFFFFF22")

    draw_centered(draw, event_title, 140, title_font, "white")
    draw_centered(draw, event_description, 290, desc_font, "white")

    y = 470
    for label, val in [("Venue:", event_venue), ("Date:", event_date), ("Time:", event_time)]:
        draw_centered(draw, f"{label} {val}", y, detail_font, "white")
        y += 80

    return img

# Generate and save posters
designs = [design_one, design_two, design_three, design_four]
for i, design_fn in enumerate(designs, 1):
    poster = design_fn()
    poster.save(os.path.join(output_dir, f"poster_{i}.png"))

print(f"Posters saved in {output_dir}")