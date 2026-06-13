import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# atmospheric pressure
atm_p = 101325 

def process_file(xlsx_path: Path) -> pd.DataFrame:
        print(f"Processing: {xlsx_path.name}")
        df = pd.read_excel(xlsx_path, engine="calamine")
        # print(f"Columns in {xlsx_path.name}: {df.columns.tolist()}")  # add this line to check column names
        df["v_dot (m3/s)"] = df["Flow_gps"] * 0.001 / 60
        df["rho_in"] = df["RTD_IN"].apply(lambda T: PropsSI("D", "T", T + 273.15, "P", atm_p, "Water"))
        df["rho_out"] = df["RTD_OUT"].apply(lambda T: PropsSI("D", "T", T + 273.15, "P", atm_p, "Water"))
        df["h_in"] = df["RTD_IN"].apply(lambda T: PropsSI("H", "T", T + 273.15, "P", atm_p, "Water"))
        df["h_out"] = df["RTD_OUT"].apply(lambda T: PropsSI("H", "T", T + 273.15, "P", atm_p, "Water"))
        df["Q"] = df["rho_in"] * df["v_dot (m3/s)"] * (df["h_in"] - df["h_out"])

        # print row number and Q value for each row to help user choose steady state range
        for row_num, row in enumerate(df.itertuples(index=False, name="Row")):
                print(f"Row {row_num}: Q value {row.Q}")

        # OR ALTERNATIVELY, plot Q vs row number to visually identify steady state range
        """plt.figure(figsize=(10, 4))
        plt.plot(df.index, df["Q"], marker="o", markersize=3)
        plt.xlabel("Row")
        plt.ylabel("Q (W)")
        plt.title(f"Q values for {xlsx_path.name}")
        plt.grid(True)
        plt.tight_layout()
        plt.show()  # pauses until you close the window"""
        
        # have user choose steady state range 
        first_steady_idx = int(input(f"Enter the first row number of the steady state range for {xlsx_path.name}: "))
        end_idx = int(input(f"Enter the END row number of steady state for {xlsx_path.name}: "))

        # show graph again with selected region highlighted
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df["Q"], marker="o", markersize=3)
        plt.axvspan(first_steady_idx, end_idx, color="green", alpha=0.3, label="steady state region")
        plt.xlabel("Row")
        plt.ylabel("Q (W)")
        plt.title(f"Q values for {xlsx_path.name} — selected steady state region")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()  # pauses until you close the window

        # average Q for the steady state range
        avg_Q_steady = df.loc[first_steady_idx:end_idx, "Q"].mean()        

        # showing which rows are in the steady state range
        df["steady_state"] = False
        df.loc[first_steady_idx:end_idx, "steady_state"] = True

        # writes avg Q of the steady state
        df["avg_Q_steady"] = None
        df.at[0, "avg_Q_steady"] = avg_Q_steady  
        
        return df

# this code is so that it runs for all of my files for this section 
for i in range (15, 35, 5):
    INPUT_FOLDER = Path(f"NURBS IDX30/Final/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER = Path(f"NURBS IDX30 PYTHON ANALYSIS/Back_final_15_2_26/{i}gps")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE = Path(f"{OUTPUT_FOLDER}/back_{i}gps_summary.xlsx")
    
    summaries = []  # collect results for each mps file here

    # creating new files and saving them
    for xlsx_file in INPUT_FOLDER.glob("*.xlsx"):
        if xlsx_file.name.startswith("~$") or not xlsx_file.stem[0].isdigit():
                continue

        result_df = process_file(xlsx_file)
       
        # extract velocity number from filename e.g. "3mps.xlsx" → 3
        velocity = int(xlsx_file.stem.replace("mps", ""))
        avg_Q = result_df.at[0, "avg_Q_steady"]
        summaries.append({"Velocity (m/s)": velocity, "Q_steady (W)": avg_Q})

        output_file = OUTPUT_FOLDER / f"{xlsx_file.stem}_analysis.xlsx"
        result_df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")

    # write summary file, sorted by velocity
    summary_df = pd.DataFrame(summaries).sort_values("Velocity (m/s)").reset_index(drop=True)
    summary_df.to_excel(SUMMARY_FILE, index=False)
    print(f"Summary saved: {SUMMARY_FILE}")




