from pathlib import Path
import pandas as pd
from analysis_code import process_file


# this first section is for the Redo_front_4_24_26
for i in range (15, 35, 5):
    INPUT_FOLDER = Path(f"NURBS IDX30/Redo_front_4_24_26/{i}gps")
    OUTPUT_FOLDER = Path(f"NURBS IDX30 PYTHON ANALYSIS/Redo_front_4_24_26/{i}gps")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE = Path(f"{OUTPUT_FOLDER}/redo_front_{i}gps_summary.xlsx")
    
    summaries = []  # collect results for each mps file here

    # creating new files and saving them
    for xlsx_file in INPUT_FOLDER.glob("*.xlsx"):
        if xlsx_file.name.startswith("~$") or not xlsx_file.stem[0].isdigit():
                continue

        result_df = process_file(xlsx_file)
       
        # extract velocity number from filename e.g. "3mps.xlsx" → 3
        velocity = int(xlsx_file.stem.replace("mps", ""))
        avg_Q = result_df.at[1, "Averages"]
        avg_Q_unc = result_df.at[3, "Averages"]
        summaries.append({"Velocity (m/s)": velocity, "Q_steady (W)": avg_Q, "Q_uncertainty (W)": avg_Q_unc})

        output_file = OUTPUT_FOLDER / f"{xlsx_file.stem}_analysis.xlsx"
        result_df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")

    # write summary file, sorted by velocity
    summary_df = pd.DataFrame(summaries).sort_values("Velocity (m/s)").reset_index(drop=True)
    summary_df.to_excel(SUMMARY_FILE, index=False)
    print(f"Summary saved: {SUMMARY_FILE}")

print("IDX30 Redo_front_4_24_26 analysis complete!")


# this section is for the original back
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
        avg_Q = result_df.at[1, "Averages"]
        avg_Q_unc = result_df.at[3, "Averages"]
        summaries.append({"Velocity (m/s)": velocity, "Q_steady (W)": avg_Q, "Q_uncertainty (W)": avg_Q_unc})

        output_file = OUTPUT_FOLDER / f"{xlsx_file.stem}_analysis.xlsx"
        result_df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")

    # write summary file, sorted by velocity
    summary_df = pd.DataFrame(summaries).sort_values("Velocity (m/s)").reset_index(drop=True)
    summary_df.to_excel(SUMMARY_FILE, index=False)
    print(f"Summary saved: {SUMMARY_FILE}")

print("IDX30 original back analysis complete!")


# this section is for the original front
for i in range (15, 35, 5):
    INPUT_FOLDER = Path(f"NURBS IDX30/Final/Front_final_15_2_26/{i}gps")
    OUTPUT_FOLDER = Path(f"NURBS IDX30 PYTHON ANALYSIS/Front_final_15_2_26/{i}gps")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE = Path(f"{OUTPUT_FOLDER}/front_{i}gps_summary.xlsx")
    
    summaries = []  # collect results for each mps file here

    # creating new files and saving them
    for xlsx_file in INPUT_FOLDER.glob("*.xlsx"):
        if xlsx_file.name.startswith("~$") or not xlsx_file.stem[0].isdigit():
                continue

        result_df = process_file(xlsx_file)
       
        # extract velocity number from filename e.g. "3mps.xlsx" → 3
        velocity = int(xlsx_file.stem.replace("mps", ""))
        avg_Q = result_df.at[1, "Averages"]
        avg_Q_unc = result_df.at[3, "Averages"]
        summaries.append({"Velocity (m/s)": velocity, "Q_steady (W)": avg_Q, "Q_uncertainty (W)": avg_Q_unc})

        output_file = OUTPUT_FOLDER / f"{xlsx_file.stem}_analysis.xlsx"
        result_df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")

    # write summary file, sorted by velocity
    summary_df = pd.DataFrame(summaries).sort_values("Velocity (m/s)").reset_index(drop=True)
    summary_df.to_excel(SUMMARY_FILE, index=False)
    print(f"Summary saved: {SUMMARY_FILE}")

print("IDX30 original front analysis complete!")
