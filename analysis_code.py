import numpy as np
import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import mplcursors


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

        # plot Q vs row number to visually identify steady state range
        fig, ax = plt.subplots(figsize=(20, 4))
        scatter = ax.plot(df.index, df["Q"], marker="o", markersize=5)
        ax.set_xlabel("Row")
        ax.tick_params(axis="x", labelsize=6)
        ax.set_xticks(np.arange(df.index.min(), df.index.max() + 1, 1))
        ax.set_ylabel("Q (W)")
        ax.set_yticks(np.arange(df["Q"].min(), df["Q"].max() + 5, 5))
        ax.set_title(f"Q values for {xlsx_path.name} — hover to see values, then close to enter range")
        ax.grid(True)
        # adds hover tooltips showing row number and Q value
        cursor = mplcursors.cursor(scatter, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
                f"Row: {sel.index}\nQ: {sel.target[1]:.2f} W"
                ))
        plt.tight_layout()
        plt.show()
        
        # have user choose steady state range 
        first_steady_idx = None
        end_idx = None
        while first_steady_idx is None or not (0 <= first_steady_idx < len(df)):
                first_steady_idx = int(input(f"Enter the first row number of the steady state range for {xlsx_path.name}: "))
        while end_idx is None or end_idx <= first_steady_idx or end_idx >= len(df):
                end_idx = int(input(f"Enter the END row number of steady state for {xlsx_path.name}: "))
                if end_idx >= len(df):
                        end_idx = len(df) - 1 # baby proofing! sets end_idx to last row if user enters a number that's too high

        # show graph again with selected region highlighted
        fig, ax = plt.subplots(figsize=(20, 4))
        scatter = ax.plot(df.index, df["Q"], marker="o", markersize=3)
        ax.axvspan(first_steady_idx, end_idx, color="green", alpha=0.3, label="steady state region")
        ax.set_xlabel("Row")
        ax.tick_params(axis="x", labelsize=6)
        ax.set_xticks(np.arange(df.index.min(), df.index.max() + 1, 1))
        ax.set_ylabel("Q (W)")
        ax.set_yticks(np.arange(df["Q"].min(), df["Q"].max() + 5, 5))
        ax.set_title(f"Q values for {xlsx_path.name} — selected steady state region")
        ax.legend()
        ax.grid(True)
        cursor = mplcursors.cursor(scatter, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
                f"Row: {sel.index}\nQ: {sel.target[1]:.2f} W"
                ))
        plt.tight_layout()
        plt.show()

        # average Q for the steady state range
        avg_Q_steady = df.loc[first_steady_idx:end_idx, "Q"].mean()        

        # showing which rows are in the steady state range
        df["steady_state"] = False
        df.loc[first_steady_idx:end_idx, "steady_state"] = True

        # writes avg Q of the steady state
        df["Averages"] = None
        df.at[0, "Averages"] = "Average Q (W)"
        df.at[1, "Averages"] = avg_Q_steady
        print(f"Average Q for steady state range in {xlsx_path.name}: {avg_Q_steady} W")

        # NOW DO UNCERTAINTY PROPAGATION
        # 0.15+0.002*RTD_value is the uncertainty of each RTD reading and 0.01 is the uncertainty of the flow rate reading from the datasheets
        df["RTD_OUT_unc"] = 0.15 + 0.002 * df["RTD_OUT"]
        df["RTD_IN_unc"] = 0.15 + 0.002 * df["RTD_IN"]
        df["RTD_unc"] = np.sqrt(df["RTD_IN_unc"]**2 + df["RTD_OUT_unc"]**2)  # combined uncertainty of the two RTDs
        df["Delta_RTD"] = df["RTD_IN"] - df["RTD_OUT"]
        df["Rel_unc"] = np.sqrt(0.01**2 + (df["RTD_unc"] / df["Delta_RTD"])**2)  # 0.01 is uncertainty of flow rate
        df["ABS_unc"] = df["Rel_unc"] * df["Q"]  # absolute uncertainty of Q = relative uncertainty of Q * Q value
        
        # writes avg Q uncertainty of the steady state range in the averages column
        avg_Q_steady_unc = df.loc[first_steady_idx:end_idx, "ABS_unc"].mean()
        df.at[2, "Averages"] = "Average Q Uncertainty (W)"
        df.at[3, "Averages"] = avg_Q_steady_unc
        print(f"Average Q uncertainty for steady state range in {xlsx_path.name}: {avg_Q_steady_unc} W")

        return df

