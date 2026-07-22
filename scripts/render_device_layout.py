#!/usr/bin/env python3
"""Render hardware/device-layout.png with unambiguous wire colors."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware" / "device-layout.png"

W, H = 1920, 1080
BG = (248, 248, 252)
BLACK = (20, 20, 20)
BLUE = (30, 90, 200)
ORANGE = (220, 120, 20)
PURPLE = (120, 60, 180)
GREEN = (30, 140, 70)
GRAY = (90, 90, 90)

# (x1,y1,x2,y2, color, width, label, label_pos)
WIRES = [
    # AC - blue
    (120, 140, 420, 140, BLUE, 5, "AC", (250, 115)),
    (420, 140, 720, 140, BLUE, 5, "AC", (540, 115)),
    (720, 140, 720, 220, BLUE, 5, "AC Always On", (730, 175)),
    (720, 140, 1050, 140, BLUE, 5, "AC Normally On", (850, 115)),
    (1050, 140, 1280, 140, BLUE, 5, "AC", (1150, 115)),
    (1280, 140, 1500, 200, BLUE, 5, "AC", (1380, 155)),
    # CT sense - orange
    (980, 170, 980, 420, ORANGE, 4, "CT", (990, 300)),
    (980, 420, 620, 420, ORANGE, 4, "CT IN", (780, 405)),
    (620, 420, 620, 500, ORANGE, 4, "CT OUT", (630, 460)),
    (620, 500, 900, 620, ORANGE, 4, "CT OUT -> GP26", (720, 555)),
    # Pico power - purple
    (760, 220, 860, 220, PURPLE, 4, "5V USB", (790, 205)),
    (860, 220, 900, 680, PURPLE, 4, "5V USB", (870, 450)),
    (900, 680, 620, 360, PURPLE, 4, "3V3", (760, 500)),
    # Trip - green
    (900, 700, 720, 280, GREEN, 4, "TRIP GP15", (780, 480)),
    # GND - black
    (620, 540, 620, 820, BLACK, 4, "GND", (630, 700)),
    (900, 760, 620, 820, BLACK, 4, "GND", (760, 800)),
    (400, 820, 1200, 820, BLACK, 4, "GND bus", (760, 835)),
    (400, 820, 400, 900, BLACK, 4, "GND", (410, 860)),
    (500, 820, 500, 900, BLACK, 4, "GND", (510, 860)),
    (600, 820, 600, 900, BLACK, 4, "GND", (610, 860)),
    # UI - purple
    (900, 720, 350, 900, PURPLE, 3, "PB GP10-12", (600, 820)),
    (900, 740, 1100, 900, PURPLE, 3, "LED GP16-18", (1000, 820)),
]

BOXES = [
    (40, 90, 200, 100, "APC UPS\nPro 1500VA"),
    (400, 90, 200, 100, "DLI IoT\nPower Relay"),
    (1000, 90, 200, 100, "PDU\n2-Post Rack"),
    (1420, 160, 180, 90, "Rack\nLoads"),
    (500, 320, 240, 220, "CT Bias Adapter\nVCC=3V3  IN=CT\nGND  OUT=CT OUT"),
    (820, 620, 220, 280, "Raspberry Pi\nPico"),
    (300, 880, 220, 120, "Learn Save\nReset PB"),
    (1040, 880, 220, 120, "Armed Tripped\nLearn LEDs"),
    (740, 180, 160, 70, "5V USB PSU"),
    (930, 120, 120, 50, "SCT-013-005\non HOT"),
]


def load_font(size):
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_dashed(draw, x1, y1, x2, y2, color, width=4, dash=12):
    import math

    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    dx, dy = (x2 - x1) / length, (y2 - y1) / length
    pos = 0
    while pos < length:
        end = min(pos + dash, length)
        draw.line(
            (x1 + dx * pos, y1 + dy * pos, x1 + dx * end, y1 + dy * end),
            fill=color,
            width=width,
        )
        pos += dash * 2


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    title_font = load_font(34)
    box_font = load_font(20)
    small_font = load_font(18)
    label_font = load_font(16)

    draw.text(
        (40, 24),
        "PDU Emergency Cutoff System — Device Layout (Wire Colors)",
        fill=BLACK,
        font=title_font,
    )

    for x1, y1, x2, y2, color, width, label, (lx, ly) in WIRES:
        if color == GREEN:
            draw_dashed(draw, x1, y1, x2, y2, color, width)
        else:
            draw.line((x1, y1, x2, y2), fill=color, width=width)
        draw.text((lx, ly), label, fill=color, font=label_font)

    for x, y, w, h, text in BOXES:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=12, outline=BLACK, width=2, fill=(255, 255, 255))
        draw.multiline_text((x + 12, y + 12), text, fill=BLACK, font=box_font, spacing=4)

    # CT adapter terminal callout
    draw.rounded_rectangle((505, 555, 735, 625), radius=8, outline=ORANGE, width=2, fill=(255, 248, 235))
    draw.text(
        (515, 565),
        "VCC (purple 3V3)  IN (orange CT)  GND (black)  OUT (orange) — separate pins",
        fill=BLACK,
        font=small_font,
    )

    # Legend
    legend_y = 980
    items = [
        (BLUE, "Blue = AC mains"),
        (ORANGE, "Orange = CT analog (IN and OUT only)"),
        (PURPLE, "Purple = 3V3, 5V USB, buttons, LEDs"),
        (BLACK, "Black = GND only"),
        (GREEN, "Green dashed = Trip GPIO (GP15)"),
    ]
    x = 40
    for color, text in items:
        draw.rectangle((x, legend_y, x + 28, legend_y + 18), fill=color)
        draw.text((x + 36, legend_y - 2), text, fill=BLACK, font=small_font)
        x += 360

    draw.text((40, 1010), "Trip: baseline 0.4 A x 1.30 = 0.52 A", fill=GRAY, font=small_font)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
