"""Imagen oficial para WhatsApp — mismo diseño que el sitio."""
import os
import io
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(__file__)
FONT_PATH = os.path.join(BASE, "assets", "fonts", "Montserrat.ttf")
LOGO_CANDIDATES = [os.path.join(BASE, "assets", "logo.png"), os.path.join(BASE, "assets", "logo_small.png")]

NAVY_TOP = (35, 32, 90)
NAVY_BOT = (7, 11, 20)
CARD = (24, 33, 52)
CARD_ALT = (20, 28, 45)
GOLD = (245, 158, 11)
GOLD2 = (250, 204, 21)
INK = (241, 245, 249)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
DIM = (51, 65, 85)
ROW_HL = {1: (92, 56, 22), 2: (52, 62, 80), 3: (70, 45, 24)}
MEDAL_COL = {1: (250, 204, 21), 2: (203, 213, 225), 3: (217, 119, 6)}

_font_cache = {}


def font(size, weight="Bold"):
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]
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
    _font_cache[key] = f
    return f


def fmt_money(val):
    try:
        return f"${int(round(val)):,}".replace(",", ".")
    except Exception:
        return "$0"


def _text_w(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b[2] - b[0]


def _center(d, cx, y, txt, f, fill):
    d.text((cx - _text_w(d, txt, f) / 2, y), txt, font=f, fill=fill)


def _right(d, rx, y, txt, f, fill):
    d.text((rx - _text_w(d, txt, f), y), txt, font=f, fill=fill)


def _circle_logo(size):
    for p in LOGO_CANDIDATES:
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                mask = Image.new("L", (size * 4, size * 4), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
                im.putalpha(mask.resize((size, size), Image.Resampling.LANCZOS))
                return im
            except Exception:
                return None
    return None


def generate_report_image(data):
    df = data["df_posiciones"]
    info = data.get("fechas_info", {})
    jugadas = [n for n in range(1, 11) if info.get(n, {}).get("registrada")]
    ultima = max(jugadas) if jugadas else None
    total_rake = data["total_rake"]
    camp, mf = data["camp_total"], data["mf_total"]
    next_ev = next((s for s in data.get("schedule_data", []) if s.get("next")), None)

    W, M = 1080, 48
    players = df.to_dict("records")
    n_rows = max(len(players), 1)
    ROW_H = 58
    head_h, pod_h, tbl_head = 190, 0, 52
    tbl_h = tbl_head + n_rows * (ROW_H + 6)
    prize_h = 250
    foot_h = 110
    H = head_h + tbl_h + prize_h + foot_h + 60

    img = Image.new("RGB", (W, H), NAVY_BOT)
    d = ImageDraw.Draw(img)
    # Fondo degradado vertical
    for y in range(H):
        t = min(1, y / (H * 0.55))
        c = tuple(int(NAVY_TOP[i] * (1 - t) + NAVY_BOT[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    # ── Header
    y = 40
    logo = _circle_logo(120)
    x_txt = M
    if logo:
        d.ellipse((M - 4, y - 4, M + 124, y + 124), fill=GOLD)
        img.paste(logo, (M, y), logo)
        x_txt = M + 150
    d.text((x_txt, y + 14), "BINGO POKER CLUB", font=font(50, "ExtraBold"), fill=GOLD2)
    d.text((x_txt, y + 76), "LIGA DE POKER · TEMPORADA 2026", font=font(22, "Bold"), fill=(203, 213, 225))
    tag = f"Tabla tras la Fecha {ultima:02d}" if ultima else "Temporada por comenzar"
    d.text((x_txt, y + 106), tag, font=font(20, "SemiBold"), fill=MUTED)
    y = head_h

    # ── Tabla
    col_pos, col_name = 64, 230
    col_tot = 120
    avail = W - 2 * M - col_pos - col_name - col_tot
    col_f = min(70, avail // max(len(jugadas), 1)) if jugadas else 0
    x_pos = M
    x_name = x_pos + col_pos
    x_f0 = x_name + col_name
    x_tot_r = W - M - 18

    d.text((x_name + 14, y + 12), "JUGADOR", font=font(18, "ExtraBold"), fill=GOLD2)
    for i, n in enumerate(jugadas):
        cx = x_f0 + i * col_f + col_f / 2
        _center(d, cx, y + 4, f"{n:02d}", font(18, "ExtraBold"), GOLD2)
        sub = info[n].get("sub") or ""
        if sub:
            _center(d, cx, y + 28, sub, font(13, "Bold"), MUTED)
    _right(d, x_tot_r, y + 12, "TOTAL", font(18, "ExtraBold"), GOLD2)
    y += tbl_head

    for idx, p in enumerate(players):
        pos = idx + 1
        bg = ROW_HL.get(pos, CARD if pos % 2 else CARD_ALT)
        d.rounded_rectangle((M, y, W - M, y + ROW_H), radius=14, fill=bg,
                            outline=GOLD if pos == 1 else None, width=2 if pos == 1 else 0)
        cy = y + ROW_H / 2
        if pos in MEDAL_COL:
            r = 17
            d.ellipse((x_pos + 30 - r, cy - r, x_pos + 30 + r, cy + r), fill=MEDAL_COL[pos])
            _center(d, x_pos + 30, cy - 13, str(pos), font(22, "ExtraBold"), (17, 24, 39))
        else:
            _center(d, x_pos + 30, cy - 13, str(pos), font(22, "Bold"), MUTED)
        d.text((x_name + 14, cy - 15), str(p["Jugador"]), font=font(25, "Bold"), fill=INK)
        for i, n in enumerate(jugadas):
            v = int(p.get(f"{n:02d}", 0))
            cx = x_f0 + i * col_f + col_f / 2
            _center(d, cx, cy - 12, str(v) if v else "·", font(21, "Bold"), GREEN if v else DIM)
        _right(d, x_tot_r, cy - 17, str(int(p.get("Total", 0))), font(31, "ExtraBold"), GOLD2)
        y += ROW_H + 6

    # ── Pozos
    y += 24
    d.rounded_rectangle((M, y, W - M, y + prize_h - 30), radius=18, fill=CARD, outline=(92, 64, 20), width=2)
    d.text((M + 28, y + 22), "RAKE TOTAL", font=font(18, "ExtraBold"), fill=MUTED)
    d.text((M + 28, y + 46), fmt_money(total_rake), font=font(44, "ExtraBold"), fill=GOLD2)
    d.text((M + 28, y + 110), f"{len(jugadas)} de 10 fechas jugadas", font=font(18, "SemiBold"), fill=MUTED)

    def prize_col(x, title, total):
        d.text((x, y + 22), title, font=font(18, "ExtraBold"), fill=GOLD2)
        d.text((x, y + 46), fmt_money(total), font=font(28, "ExtraBold"), fill=INK)
        for j, (lbl, pct) in enumerate([("1º", .5), ("2º", .3), ("3º", .2)]):
            yy = y + 96 + j * 34
            d.text((x, yy), lbl, font=font(20, "Bold"), fill=MUTED)
            d.text((x + 50, yy), fmt_money(total * pct), font=font(22, "Bold"), fill=INK)

    prize_col(M + 380, "CAMPEONATO 50%", camp)
    prize_col(M + 690, "MESA FINAL 40%", mf)
    y += prize_h

    # ── Footer
    if next_ev:
        txt = f"Próxima: {next_ev['fecha']} · {next_ev['desc']}"
    elif data.get("evento_final"):
        txt = f"Mesa Final: {data['evento_final']}"
    else:
        txt = ""
    if txt:
        tw = _text_w(d, txt, font(24, "Bold")) + 56
        x0 = (W - tw) / 2
        d.rounded_rectangle((x0, y, x0 + tw, y + 52), radius=26, fill=GOLD)
        _center(d, W / 2, y + 12, txt, font(24, "Bold"), (17, 24, 39))
    _center(d, W / 2, H - 44, "bingopoker.streamlit.app", font(18, "SemiBold"), MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
