"""Imagen oficial para WhatsApp — pensada para leerse en el celular (vertical, letra grande)."""
import os
import io
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(__file__)
FONT_PATH = os.path.join(BASE, "assets", "fonts", "Montserrat.ttf")
LOGO_CANDIDATES = [os.path.join(BASE, "assets", "logo.png"), os.path.join(BASE, "assets", "logo_small.png")]

BG_TOP = (38, 34, 98)
BG_BOT = (8, 12, 24)
CARD = (25, 34, 54)
CARD2 = (20, 28, 46)
GOLD = (245, 158, 11)
GOLD2 = (250, 204, 21)
INK = (241, 245, 249)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
DARK = (17, 24, 39)
MEDAL = {1: ((253, 230, 138), (245, 158, 11)), 2: ((241, 245, 249), (148, 163, 184)), 3: ((253, 186, 116), (180, 83, 9))}

_fc = {}


def font(size, weight="Bold"):
    k = (size, weight)
    if k not in _fc:
        try:
            f = ImageFont.truetype(FONT_PATH, size)
            try:
                f.set_variation_by_name(weight)
            except Exception:
                pass
        except Exception:
            try:
                f = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
            except Exception:
                f = ImageFont.load_default()
        _fc[k] = f
    return _fc[k]


def fmt_money(v):
    try:
        return f"${int(round(v)):,}".replace(",", ".")
    except Exception:
        return "$0"


def tw(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def center(d, cx, y, t, f, fill):
    d.text((cx - tw(d, t, f) / 2, y), t, font=f, fill=fill)


def right(d, rx, y, t, f, fill):
    d.text((rx - tw(d, t, f), y), t, font=f, fill=fill)


def fit(d, t, f_size, max_w, weight="Bold"):
    """Achica la fuente si un nombre largo no cabe."""
    s = f_size
    while s > 18 and tw(d, t, font(s, weight)) > max_w:
        s -= 2
    return font(s, weight)


def medal(img, cx, cy, r, pos):
    d = ImageDraw.Draw(img)
    if pos in MEDAL:
        top, bot = MEDAL[pos]
        for i in range(r, 0, -1):
            t = i / r
            c = tuple(int(top[k] * t + bot[k] * (1 - t)) for k in range(3))
            d.ellipse((cx - i, cy - i, cx + i, cy + i), fill=c)
        f = font(int(r * 1.15), "ExtraBold")
        b = d.textbbox((0, 0), str(pos), font=f)
        d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), str(pos), font=f, fill=DARK)
    else:
        f = font(int(r * 1.1), "Bold")
        b = d.textbbox((0, 0), str(pos), font=f)
        d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), str(pos), font=f, fill=MUTED)


def circle_logo(size):
    for p in LOGO_CANDIDATES:
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                m = Image.new("L", (size * 4, size * 4), 0)
                ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
                im.putalpha(m.resize((size, size), Image.Resampling.LANCZOS))
                return im
            except Exception:
                return None
    return None


def generate_report_image(data):
    df = data["df_posiciones"]
    info = data.get("fechas_info", {})
    jugadas = [n for n in range(1, 11) if info.get(n, {}).get("registrada")]
    ultima = max(jugadas) if jugadas else None
    camp, mf = data["camp_total"], data["mf_total"]
    next_ev = next((s for s in data.get("schedule_data", []) if s.get("next")), None)
    players = df.to_dict("records")
    resto = players[3:]

    W, M = 1080, 56
    ROW = 92
    H = 330 + 380 + len(resto) * (ROW + 12) + 60 + 330 + 200
    img = Image.new("RGB", (W, H), BG_BOT)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = min(1, y / (H * 0.5))
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3)))

    # ── Encabezado
    y = 48
    logo = circle_logo(150)
    if logo:
        d.ellipse((W / 2 - 80, y - 5, W / 2 + 80, y + 155), fill=GOLD)
        img.paste(logo, (int(W / 2 - 75), y), logo)
    y += 175
    center(d, W / 2, y, "BINGO POKER CLUB", font(58, "ExtraBold"), GOLD2)
    y += 76
    tag = f"POSICIONES TRAS LA FECHA {ultima:02d}" if ultima else "TEMPORADA 2026"
    f = font(26, "Bold")
    w = tw(d, tag, f) + 50
    d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 48), radius=24, outline=GOLD, width=2)
    center(d, W / 2, y + 9, tag, f, INK)
    y += 90

    # ── Podio (2º · 1º · 3º)
    cw, gap = 300, 26
    xs = [M, M + cw + gap, M + 2 * (cw + gap)]
    order = [(1, xs[0], 60), (0, xs[1], 0), (2, xs[2], 60)]
    for i, x, off in order:
        if i >= len(players):
            continue
        p = players[i]
        top = y + off
        h = 330 - off
        first = i == 0
        d.rounded_rectangle((x, top, x + cw, top + h), radius=26, fill=(70, 45, 22) if first else CARD,
                            outline=GOLD if first else (60, 72, 96), width=4 if first else 2)
        r = 46 if first else 38
        medal(img, x + cw / 2, top + 26 + r, r, i + 1)
        ny = top + 40 + 2 * r
        center(d, x + cw / 2, ny, str(p["Jugador"]), fit(d, str(p["Jugador"]), 40 if first else 36, cw - 30), INK)
        center(d, x + cw / 2, ny + 54, f"{int(p['Total'])}", font(64 if first else 54, "ExtraBold"), GOLD2)
        center(d, x + cw / 2, ny + (128 if first else 116), "puntos", font(22, "SemiBold"), MUTED)
    y += 360

    # ── Resto de la tabla
    for idx, p in enumerate(resto):
        pos = idx + 4
        d.rounded_rectangle((M, y, W - M, y + ROW), radius=20, fill=CARD if idx % 2 == 0 else CARD2)
        cy = y + ROW / 2
        medal(img, M + 50, cy, 26, pos)
        d.text((M + 100, cy - 24), str(p["Jugador"]), font=fit(d, str(p["Jugador"]), 40, 520), fill=INK)
        lv = int(p.get(f"{ultima:02d}", 0)) if ultima else 0
        if lv:
            right(d, W - M - 190, cy - 16, f"+{lv}", font(30, "Bold"), GREEN)
        right(d, W - M - 30, cy - 30, f"{int(p['Total'])}", font(52, "ExtraBold"), GOLD2)
        y += ROW + 12
    if resto:
        d.text((M + 10, y), f"+pts = sumados en la Fecha {ultima:02d}", font=font(20, "SemiBold"), fill=MUTED)
    y += 60

    # ── Premios
    pw = (W - 2 * M - 24) / 2
    for k, (title, total) in enumerate([("CAMPEONATO", camp), ("MESA FINAL", mf)]):
        x = M + k * (pw + 24)
        d.rounded_rectangle((x, y, x + pw, y + 300), radius=24, fill=CARD, outline=(110, 76, 22), width=2)
        d.text((x + 30, y + 26), title, font=font(26, "ExtraBold"), fill=GOLD2)
        d.text((x + 30, y + 62), fmt_money(total), font=font(46, "ExtraBold"), fill=INK)
        for j, pct in enumerate([.5, .3, .2]):
            yy = y + 140 + j * 50
            medal(img, x + 50, yy + 18, 20, j + 1)
            right(d, x + pw - 30, yy, fmt_money(total * pct), font(34, "Bold"), INK)
    y += 340

    # ── Próxima fecha
    if next_ev:
        txt = f"Próxima: {next_ev['fecha']} · {next_ev['desc']}"
    elif data.get("evento_final"):
        txt = f"Mesa Final: {data['evento_final']}"
    else:
        txt = ""
    if txt:
        f = font(28, "Bold")
        while tw(d, txt, f) > W - 2 * M - 60 and f.size > 18:
            f = font(f.size - 2, "Bold")
        w = tw(d, txt, f) + 60
        d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 64), radius=32, fill=GOLD)
        center(d, W / 2, y + 15, txt, f, DARK)
    center(d, W / 2, H - 62, "Tabla completa en bingopoker.streamlit.app", font(24, "SemiBold"), MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def whatsapp_text(data):
    """Resumen en texto con formato de WhatsApp (negritas con *)."""
    df = data["df_posiciones"]
    info = data.get("fechas_info", {})
    jugadas = [n for n in range(1, 11) if info.get(n, {}).get("registrada")]
    ultima = max(jugadas) if jugadas else None
    camp, mf = data["camp_total"], data["mf_total"]
    med = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = ["🏆 *BINGO POKER CLUB 2026*"]
    if ultima:
        lines.append(f"Posiciones tras la Fecha {ultima:02d}")
    lines.append("")
    for i, p in enumerate(df.to_dict("records")):
        pos = i + 1
        lv = int(p.get(f"{ultima:02d}", 0)) if ultima else 0
        extra = f" (+{lv})" if lv else ""
        lines.append(f"{med.get(pos, f'{pos}.')} *{p['Jugador']}* — {int(p['Total'])} pts{extra}")
    lines += ["",
              f"💰 *Campeonato {fmt_money(camp)}*",
              f"1º {fmt_money(camp * .5)} · 2º {fmt_money(camp * .3)} · 3º {fmt_money(camp * .2)}",
              f"🃏 *Mesa Final {fmt_money(mf)}*",
              f"1º {fmt_money(mf * .5)} · 2º {fmt_money(mf * .3)} · 3º {fmt_money(mf * .2)}"]
    nxt = next((s for s in data.get("schedule_data", []) if s.get("next")), None)
    if nxt:
        lines += ["", f"📅 Próxima: *{nxt['fecha']}* · {nxt['desc']}"]
    lines += ["", "👉 bingopoker.streamlit.app"]
    return "\n".join(lines)
