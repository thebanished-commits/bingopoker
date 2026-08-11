import os
import io
from PIL import Image, ImageDraw, ImageFont

REL_LOGO = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
ALT_LOGO_PATH = r'C:\programas\poker\logo.jpeg'

if os.path.exists(REL_LOGO):
    LOGO_PATH = REL_LOGO
elif os.path.exists(ALT_LOGO_PATH):
    LOGO_PATH = ALT_LOGO_PATH
else:
    LOGO_PATH = None

def fmt_money(val):
    try:
        return f"${int(val):,}".replace(",", ".")
    except Exception:
        return "$0"

def get_font(size, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", 
                  "segoeui.ttf", "tahoma.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def generate_report_image(data):
    df_pos = data["df_posiciones"]
    subheaders = data.get("subheaders", ["FR"] + [""] * 9)
    total_rake = data["total_rake"]
    
    # 50% Campeonato, 40% Mesa Final
    camp_total = total_rake * 0.50
    mf_total = total_rake * 0.40
    
    payouts = [
        {"Pos": 1, "Campeonato": int(camp_total * 0.50), "Mesa Final": int(mf_total * 0.50)},
        {"Pos": 2, "Campeonato": int(camp_total * 0.30), "Mesa Final": int(mf_total * 0.30)},
        {"Pos": 3, "Campeonato": int(camp_total * 0.20), "Mesa Final": int(mf_total * 0.20)},
    ]
    
    S = 2
    
    NAVY_HEADER = (27, 54, 93)
    LIGHT_BLUE = (104, 151, 187)
    TOTAL_BG = (140, 180, 214)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    GRID_COLOR = (40, 40, 40)
    
    f_title = get_font(20 * S, bold=True)
    f_header = get_font(13 * S, bold=True)
    f_sub = get_font(11 * S, bold=True)
    f_cell = get_font(12 * S, bold=True)
    f_num = get_font(12 * S, bold=True)
    
    col_w_pos = 45 * S
    col_w_name = 110 * S
    col_w_fecha = 50 * S
    col_w_f = 32 * S
    col_w_tot = 55 * S
    
    n_fechas = 10
    main_tbl_width = col_w_pos + col_w_name + col_w_fecha + (col_w_f * n_fechas) + col_w_tot
    
    row_h_title = 40 * S
    row_h_hdr1 = 28 * S
    row_h_hdr2 = 22 * S
    row_h_data = 28 * S
    
    n_rows = max(len(df_pos), 7)
    main_tbl_height = row_h_title + row_h_hdr1 + row_h_hdr2 + (row_h_data * n_rows)
    
    side_w = 260 * S
    gap = 25 * S
    
    img_w = main_tbl_width + side_w + 320 * S
    img_h = main_tbl_height + 40 * S
    
    img = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x0 = 15 * S
    y0 = 15 * S
    
    draw.rectangle([x0, y0, x0 + main_tbl_width, y0 + row_h_title], fill=NAVY_HEADER, outline=GRID_COLOR, width=S)
    
    bbox = draw.textbbox((0, 0), "Bingo Poker Club", font=f_title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x0 + (main_tbl_width - tw) / 2, y0 + (row_h_title - th) / 2 - 2*S), "Bingo Poker Club", fill=YELLOW, font=f_title)
    
    y_h1 = y0 + row_h_title
    
    draw.rectangle([x0, y_h1, x0 + main_tbl_width - col_w_tot, y_h1 + row_h_hdr1 + row_h_hdr2], fill=LIGHT_BLUE, outline=GRID_COLOR, width=S)
    draw.rectangle([x0 + main_tbl_width - col_w_tot, y_h1, x0 + main_tbl_width, y_h1 + row_h_hdr1 + row_h_hdr2], fill=TOTAL_BG, outline=GRID_COLOR, width=S)
    
    cx_pos = x0
    cx_name = cx_pos + col_w_pos
    cx_fecha = cx_name + col_w_name
    cx_f0 = cx_fecha + col_w_fecha
    
    draw.text((cx_pos + 6*S, y_h1 + 10*S), "Pos.", fill=YELLOW, font=f_header)
    draw.text((cx_name + 8*S, y_h1 + 10*S), "Jugador", fill=YELLOW, font=f_header)
    draw.text((cx_fecha + 4*S, y_h1 + 10*S), "Fecha", fill=YELLOW, font=f_header)
    
    for i in range(10):
        f_lbl = f"{i+1:02d}"
        fx = cx_f0 + (i * col_w_f)
        draw.text((fx + 6*S, y_h1 + 4*S), f_lbl, fill=YELLOW, font=f_header)
        
        sub_txt = subheaders[i] if i < len(subheaders) else ""
        if sub_txt:
            draw.text((fx + 5*S, y_h1 + row_h_hdr1 + 2*S), sub_txt, fill=WHITE, font=f_sub)
            
    draw.text((cx_f0 + 10 * col_w_f + 8*S, y_h1 + 10*S), "Total", fill=YELLOW, font=f_header)
    
    draw.line([cx_name, y_h1, cx_name, y_h1 + row_h_hdr1 + row_h_hdr2], fill=GRID_COLOR, width=S)
    draw.line([cx_fecha, y_h1, cx_fecha, y_h1 + row_h_hdr1 + row_h_hdr2], fill=GRID_COLOR, width=S)
    draw.line([cx_f0, y_h1, cx_f0, y_h1 + row_h_hdr1 + row_h_hdr2], fill=GRID_COLOR, width=S)
    for i in range(1, 11):
        fx = cx_f0 + (i * col_w_f)
        draw.line([fx, y_h1, fx, y_h1 + row_h_hdr1 + row_h_hdr2], fill=GRID_COLOR, width=S)
        
    draw.line([cx_f0, y_h1 + row_h_hdr1, cx_f0 + 10 * col_w_f, y_h1 + row_h_hdr1], fill=GRID_COLOR, width=S)
    
    y_curr = y_h1 + row_h_hdr1 + row_h_hdr2
    
    records = df_pos.to_dict('records')
    for r_idx in range(n_rows):
        p = records[r_idx] if r_idx < len(records) else None
        
        bg_col = WHITE
        draw.rectangle([x0, y_curr, x0 + main_tbl_width - col_w_tot, y_curr + row_h_data], fill=bg_col, outline=GRID_COLOR, width=S)
        draw.rectangle([x0 + main_tbl_width - col_w_tot, y_curr, x0 + main_tbl_width, y_curr + row_h_data], fill=TOTAL_BG, outline=GRID_COLOR, width=S)
        
        if p:
            draw.text((cx_pos + 15*S, y_curr + 4*S), str(r_idx + 1), fill=BLACK, font=f_cell)
            draw.text((cx_name + 8*S, y_curr + 4*S), str(p["Jugador"]), fill=BLACK, font=f_cell)
            
            for i in range(10):
                f_key = f"{i+1:02d}"
                val = p.get(f_key, 0)
                val_str = str(int(val))
                fx = cx_f0 + (i * col_w_f)
                draw.text((fx + 8*S, y_curr + 4*S), val_str, fill=BLACK, font=f_num)
                
            tot_val = str(int(p.get("Total", 0)))
            draw.text((cx_f0 + 10 * col_w_f + 12*S, y_curr + 4*S), tot_val, fill=BLACK, font=f_cell)
        else:
            draw.text((cx_pos + 15*S, y_curr + 4*S), str(r_idx + 1), fill=BLACK, font=f_cell)
            
        draw.line([cx_name, y_curr, cx_name, y_curr + row_h_data], fill=GRID_COLOR, width=S)
        draw.line([cx_fecha, y_curr, cx_fecha, y_curr + row_h_data], fill=GRID_COLOR, width=S)
        draw.line([cx_f0, y_curr, cx_f0, y_curr + row_h_data], fill=GRID_COLOR, width=S)
        for i in range(1, 11):
            fx = cx_f0 + (i * col_w_f)
            draw.line([fx, y_curr, fx, y_curr + row_h_data], fill=GRID_COLOR, width=S)
            
        y_curr += row_h_data

    x_side = x0 + main_tbl_width + gap
    y_side = y0
    
    draw.rectangle([x_side, y_side, x_side + side_w, y_side + row_h_hdr1], fill=NAVY_HEADER, outline=GRID_COLOR, width=S)
    bbox = draw.textbbox((0, 0), "Ganancias Totales", font=f_header)
    tw = bbox[2] - bbox[0]
    draw.text((x_side + (side_w - tw)/2, y_side + 5*S), "Ganancias Totales", fill=YELLOW, font=f_header)
    
    y_side += row_h_hdr1
    draw.rectangle([x_side, y_side, x_side + side_w, y_side + row_h_data], fill=WHITE, outline=GRID_COLOR, width=S)
    val_str = fmt_money(total_rake)
    bbox = draw.textbbox((0, 0), val_str, font=f_cell)
    tw = bbox[2] - bbox[0]
    draw.text((x_side + (side_w - tw)/2, y_side + 4*S), val_str, fill=BLACK, font=f_cell)
    
    y_side += row_h_data + 20 * S
    
    w_p_pos = 75 * S
    w_p_camp = 95 * S
    w_p_mf = 90 * S
    
    draw.rectangle([x_side, y_side, x_side + w_p_pos, y_side + row_h_hdr1], fill=NAVY_HEADER, outline=GRID_COLOR, width=S)
    draw.rectangle([x_side + w_p_pos, y_side, x_side + w_p_pos + w_p_camp, y_side + row_h_hdr1], fill=NAVY_HEADER, outline=GRID_COLOR, width=S)
    draw.rectangle([x_side + w_p_pos + w_p_camp, y_side, x_side + side_w, y_side + row_h_hdr1], fill=NAVY_HEADER, outline=GRID_COLOR, width=S)
    
    draw.text((x_side + 6*S, y_side + 5*S), "Posiciones", fill=YELLOW, font=f_header)
    draw.text((x_side + w_p_pos + 4*S, y_side + 5*S), "Campeonato", fill=YELLOW, font=f_header)
    draw.text((x_side + w_p_pos + w_p_camp + 8*S, y_side + 5*S), "Mesa Final", fill=YELLOW, font=f_header)
    
    y_side += row_h_hdr1
    
    for pay in payouts:
        pos_num = str(pay["Pos"])
        c_amt = fmt_money(pay["Campeonato"])
        m_amt = fmt_money(pay["Mesa Final"])
        
        draw.rectangle([x_side, y_side, x_side + w_p_pos, y_side + row_h_data], fill=LIGHT_BLUE, outline=GRID_COLOR, width=S)
        draw.rectangle([x_side + w_p_pos, y_side, x_side + side_w, y_side + row_h_data], fill=WHITE, outline=GRID_COLOR, width=S)
        
        draw.text((x_side + 30*S, y_side + 4*S), pos_num, fill=YELLOW, font=f_header)
        
        bbox_c = draw.textbbox((0, 0), c_amt, font=f_cell)
        tw_c = bbox_c[2] - bbox_c[0]
        draw.text((x_side + w_p_pos + w_p_camp - tw_c - 10*S, y_side + 4*S), c_amt, fill=BLACK, font=f_cell)
        
        bbox_m = draw.textbbox((0, 0), m_amt, font=f_cell)
        tw_m = bbox_m[2] - bbox_m[0]
        draw.text((x_side + side_w - tw_m - 10*S, y_side + 4*S), m_amt, fill=BLACK, font=f_cell)
        
        draw.line([x_side + w_p_pos + w_p_camp, y_side, x_side + w_p_pos + w_p_camp, y_side + row_h_data], fill=GRID_COLOR, width=S)
        
        y_side += row_h_data

    x_logo = x_side + side_w + 20 * S
    y_logo = y0
    
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            logo_img = Image.open(LOGO_PATH).convert("RGBA")
            logo_size = int(main_tbl_height * 0.95)
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            img.paste(logo_img, (x_logo, y_logo + 5*S), logo_img)
        except Exception as e:
            print("Logo rendering error:", e)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
