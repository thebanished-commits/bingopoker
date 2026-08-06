import pandas as pd
import openpyxl
import os
import shutil

LOCAL_EXCEL = r'C:\programas\poker\bingo poker club 2026.xlsx'
REL_EXCEL = os.path.join(os.path.dirname(__file__), 'bingo poker club 2026.xlsx')

if os.path.exists(LOCAL_EXCEL):
    EXCEL_PATH = LOCAL_EXCEL
else:
    EXCEL_PATH = REL_EXCEL

POINTS_RULES = {
    "Torneo Regular Shorthanded (SH)": {1: 30, 2: 10, 3: 0, 4: 0, 5: 0},
    "Torneo Regular Full ring (FR)": {1: 50, 2: 35, 3: 20, 4: 10, 5: 0},
    "Torneo Regular Multitable (MM)": {1: 70, 2: 50, 3: 30, 4: 20, 5: 0},
    "Main Event Shorthanded (SH)": {1: 70, 2: 30, 3: 0, 4: 0, 5: 0},
    "Main Event Full ring (FR)": {1: 100, 2: 75, 3: 40, 4: 20, 5: 10},
    "Main Event Multitable (MM)": {1: 130, 2: 90, 3: 50, 4: 35, 5: 20},
}

FECHAS_STANDARD = [f"{i:02d}" for i in range(1, 11)]

def create_backup():
    if os.path.exists(EXCEL_PATH):
        backup_path = EXCEL_PATH.replace('.xlsx', '_backup.xlsx')
        try:
            shutil.copy(EXCEL_PATH, backup_path)
            return backup_path
        except Exception as e:
            print("Backup warning:", e)
    return None

def load_data():
    create_backup()
    xl = pd.ExcelFile(EXCEL_PATH)
    
    df_pos_raw = xl.parse('Posiciones', header=None)
    subheaders = [str(x) if not pd.isna(x) else "" for x in df_pos_raw.iloc[3, 4:14].values]
    
    players_data = []
    for idx in range(4, len(df_pos_raw)):
        row = df_pos_raw.iloc[idx]
        pos = row[1]
        player = row[2]
        if pd.isna(player) or str(player).strip() == "":
            continue
        
        pts = {}
        for col_i, f_name in enumerate(FECHAS_STANDARD):
            val = row[4 + col_i]
            pts[f_name] = int(float(val)) if not pd.isna(val) else 0
            
        total_pts = sum(pts.values())
        players_data.append({
            "Pos": int(pos) if not pd.isna(pos) else len(players_data) + 1,
            "Jugador": str(player).strip(),
            **pts,
            "Total": total_pts
        })
        
    df_pos = pd.DataFrame(players_data)
    if not df_pos.empty:
        df_pos = df_pos.sort_values(by="Total", ascending=False).reset_index(drop=True)
        df_pos["Pos"] = range(1, len(df_pos) + 1)
        
    for f in FECHAS_STANDARD:
        if f not in df_pos.columns:
            df_pos[f] = 0
            
    cols_order = ["Pos", "Jugador"] + FECHAS_STANDARD + ["Total"]
    df_pos = df_pos[cols_order]

    df_rake_raw = xl.parse('rake', header=None)
    rake_cols = [f"F{i}" for i in range(1, 11)]
    rake_vals = [float(x) if not pd.isna(x) else 0.0 for x in df_rake_raw.iloc[2, 1:11].values]
    
    rake_dict = dict(zip(rake_cols, rake_vals))
    total_rake = sum(rake_vals)
    
    # Updated distribution: 50% Campeonato, 40% Mesa Final, 10% Gastos Mesa Final
    camp_total = total_rake * 0.50
    mf_total = total_rake * 0.40
    gastos_mf = total_rake * 0.10
    
    payouts = [
        {"Pos": 1, "Campeonato": int(camp_total * 0.50), "Mesa Final": int(mf_total * 0.50)},
        {"Pos": 2, "Campeonato": int(camp_total * 0.30), "Mesa Final": int(mf_total * 0.30)},
        {"Pos": 3, "Campeonato": int(camp_total * 0.20), "Mesa Final": int(mf_total * 0.20)},
    ]
    
    return {
        "df_posiciones": df_pos,
        "fechas_headers": FECHAS_STANDARD,
        "subheaders": subheaders,
        "rake_dict": rake_dict,
        "total_rake": total_rake,
        "camp_total": camp_total,
        "mf_total": mf_total,
        "gastos_mf": gastos_mf,
        "payouts": payouts
    }

def save_data(df_posiciones, rake_dict, subheaders_list=None):
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws_pos = wb['Posiciones']
    
    if subheaders_list:
        for c_idx, sub in enumerate(subheaders_list):
            ws_pos.cell(row=4, column=5 + c_idx, value=sub if sub else None)
            
    for r in range(5, 25):
        ws_pos.cell(row=r, column=2, value=None)
        ws_pos.cell(row=r, column=3, value=None)
        for c in range(5, 15):
            ws_pos.cell(row=r, column=c, value=None)
        ws_pos.cell(row=r, column=15, value=None)
        
    for row_idx, p_data in enumerate(df_posiciones.to_dict('records')):
        r_num = 5 + row_idx
        ws_pos.cell(row=r_num, column=2, value=row_idx + 1)
        ws_pos.cell(row=r_num, column=3, value=p_data['Jugador'])
        
        tot = 0
        for c_idx, f_name in enumerate(FECHAS_STANDARD):
            v = p_data.get(f_name, 0)
            ws_pos.cell(row=r_num, column=5 + c_idx, value=int(v) if v > 0 else None)
            tot += v
            
        ws_pos.cell(row=r_num, column=15, value=tot)
        
    ws_rake = wb['rake']
    total_r = 0
    for c_idx, f_name in enumerate([f'F{i}' for i in range(1, 11)]):
        val = rake_dict.get(f_name, 0)
        ws_rake.cell(row=3, column=2 + c_idx, value=float(val) if val > 0 else None)
        total_r += val
    ws_rake.cell(row=3, column=12, value=total_r if total_r > 0 else None)
    
    ws_pos.cell(row=3, column=17, value=total_r)
    
    camp_tot = total_r * 0.50
    mf_tot = total_r * 0.40
    payout_dist = [(0.50, 0.50), (0.30, 0.30), (0.20, 0.20)]
    for idx, (p_camp, p_mf) in enumerate(payout_dist):
        ws_pos.cell(row=5 + idx, column=18, value=int(camp_tot * p_camp))
        ws_pos.cell(row=5 + idx, column=19, value=int(mf_tot * p_mf))
        
    wb.save(EXCEL_PATH)
    return True
