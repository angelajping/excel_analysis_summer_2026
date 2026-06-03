import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import pandas as pd
from pathlib import Path

# atmospheric pressure
atm_p = 101325 

def process_file(xlsx_path: Path) -> pd.DataFrame:
        df = pd.read_excel(xlsx_path)
        df["v_dot (m3/s)"] = df["Flow_gps"] * 0.001 / 60
        df["rho_in"] = df["RTD_IN"].apply(lambda T: PropsSI("D", "T", T + 273.15, "P", atm_p, "Water"))
        df["rho_out"] = df["RTD_OUT"].apply(lambda T: PropsSI("D", "T", T + 273.15, "P", atm_p, "Water"))
        df["h_in"] = df["RTD_IN"].apply(lambda T: PropsSI("H", "T", T + 273.15, "P", atm_p, "Water"))
        df["h_out"] = df["RTD_OUT"].apply(lambda T: PropsSI("H", "T", T + 273.15, "P", atm_p, "Water"))
        df["Q"] = df["rho_in"] * df["v_dot (m3/s)"] * (df["h_out"] - df["h_in"])

        STEADY_THRESHOLD = 0.5  # tune this if needed
        rolling_std = df["Q"].rolling(window=5).std()
        steady_mask = rolling_std < STEADY_THRESHOLD
        avg_Q_steady = df.loc[steady_mask, "Q"].mean()
        print(f"{i}gps — Steady rows: {steady_mask.sum()} / {len(df)}, Avg Q: {avg_Q_steady:.4f}")
        # append label and value into column W
        label_row = {col: None for col in df.columns}
        value_row = {col: None for col in df.columns}
        label_row["Q"] = "average steady state Q"
        value_row["Q"] = avg_Q_steady

        df = pd.concat([df, pd.DataFrame([label_row, value_row])], ignore_index=True)
        
        return df

for i in range (15, 35, 5):
    INPUT_FOLDER = Path(f"Desktop/Research/NURBS IDX30/Final/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER = Path(f"Desktop/Research/NURBS IDX30 PYTHON ANALYSIS/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE = Path(f"{OUTPUT_FOLDER}/Back_{i}gps_Analysis.xlsx")




