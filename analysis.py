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

        # CALCULATING STEADY STATE THRESHOLD 
        STEADY_THRESHOLD = 1.5          # this is a guess that should probably be tweaked
        WINDOW = 5
        rolling_std = df["Q"].rolling(window=WINDOW).std()
        steady_mask = rolling_std < STEADY_THRESHOLD
        end_idx = df.index[-1]
        start_idx = end_idx

        # while the index is not 0 and the data point is "steady", this loop runs
        while start_idx >= 0 and steady_mask.loc[start_idx]:
                start_idx -= 1
        # to get correct starting index where it is steady, add 1 
        start_idx += 1
        # find average Q in the steady state range
        avg_Q_steady = df.loc[start_idx:end_idx, "Q"].mean()

        # for debugging
        print(
                f"{i}gps — Final steady region rows {start_idx+2}:{end_idx+2}, "
                f"Avg Q: {avg_Q_steady:.4f}"
        )

        # shows which rows are marked true and false for steady state
        df["steady_state"] = False
        df.loc[start_idx:end_idx, "steady_state"] = True
        # writes avg Q of the steady state
        df["avg_Q_steady"] = avg_Q_steady       
        
        return df

# this code is so that it runs for all of my files for this section 
for i in range (15, 35, 5):
    INPUT_FOLDER = Path(f"Desktop/Research/NURBS IDX30/Final/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER = Path(f"Desktop/Research/NURBS IDX30 PYTHON ANALYSIS/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE = Path(f"{OUTPUT_FOLDER}/Back_{i}gps_Analysis.xlsx")
    
    # creating new files and saving them
    for xlsx_file in INPUT_FOLDER.glob("*.xlsx"):
        result_df = process_file(xlsx_file)
        output_file = OUTPUT_FOLDER / f"{xlsx_file.stem}_analysis.xlsx"
        result_df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")




