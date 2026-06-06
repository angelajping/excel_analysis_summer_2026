import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import pandas as pd
from pathlib import Path

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

        # CALCULATING STEADY STATE THRESHOLD 
        STEADY_THRESHOLD = 3         # this is a guess that should probably be tweaked
        WINDOW = 3
        rolling_std = df["Q"].rolling(window=WINDOW).std()
        steady_mask = rolling_std < STEADY_THRESHOLD

        # find first TRUE in bottom half, average from there to end
        halfway = len(df) // 2
        bottom_half_true = steady_mask[halfway:][steady_mask[halfway:] == True]

        if not bottom_half_true.empty:
                first_steady_idx = bottom_half_true.index[0]
                avg_Q_steady = df.loc[first_steady_idx:, "Q"].mean()
        else:  # no steady rows at all — average everything
                first_steady_idx = None
                avg_Q_steady = df["Q"].mean()
                print(f"  Warning: no steady rows found in {xlsx_path.name} — averaging all rows")

        # for debugging
        rows_used = f"{first_steady_idx+2} to {len(df)+1}" if first_steady_idx is not None else "all rows"
        print(
                f"{i}gps — Steady rows: {steady_mask.sum()} / {len(df)}, "
                f"Avg Q: {avg_Q_steady:.4f}, "
                f"Rows used: {rows_used}"
        )

        
        # THIS IS THE BACKWARDS UP WAY
        """
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
        """

        # shows the rolling standard deviation of Q, which is used to determine steady state
        df["rolling_std"] = df["Q"].rolling(window=WINDOW).std()
        # shows which rows are marked true and false for steady state
        df["steady_state"] = False
        df.loc[steady_mask, "steady_state"] = True
        """df.loc[start_idx:end_idx, "steady_state"] = True # for the backwards up way, this marks the steady state rows as true"""
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




