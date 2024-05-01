"""
UKCP18 Flow Statistics
Ben Smith
09/01/2023
Newcastle University

--- NOTES -------------------------------
All drought data is for the described period. It is not normalised to the length
of the period (the baseline period is shorter than future periods).

Lower in the script you will need to add / uncomment the chosen output name and file paths.

Flows that cannot have lmoments (i.e. return periods) calculated will be set at 0 cumecs.
This is because many of the instances where the calculation fails is where the flows are 0, so 0 cumecs
flow events makes sense. However! This may mask errors where flows are expected, so best to check this
when the errors are flagged.
This may be due to large numbers of 0 values in the flows. E.g. 02c 33023, which becomes highly ephemeral.

Run this on Blade 4 using:
conda activate \ProgramData\Water_Blade_Programs\BenSmith\env_lmoments
I:
cd "SHETRAN_GB_2021\08_Analysis\03 - Flow Analysis"
python "Hydrological Flow and Drought Analysis - Catchments.py" REM 'add any comment you want here'

Ben also has an environment called lmoments on his laptop that works.

--- Lmoments3----------------------------
This analysis requires Lmoments3 - this conflicts with Xarray in my environment. You may need to create an environment
for this potentially removing other modules (e.g. conda remove xarray). Installation instructions are here:
https://anaconda.org/openhydrology/lmoments3 - conda install -c openhydrology lmoments3
This method did not work well, and so 'pip install lmoments3' was used, which did work. You may first have to install
pip (conda install pip), then it may be best to use 'python -m pip install lmoments3' so that it uses the conda python,
not the pip python.

Within SHETRAN each element has four faces, numbered 1 (east), 2 (north), 3 (west), 4 (south).
BUT the h5 outputs are in the order north, east, south, west - for python, these are [0,1,2,3].
For water flow in Shetran: any flow in a northerly or easterly direction is +ve and any
flow in a Southerly or westerly direction is -ve.

--- TODO: -------------------------------
        - DROUGHTS ARE WRONG AND NEED UPDATING FROM THE CATCHMENT CODE

      - Consider whether you should be calculating intensity and severity non-standardised and only using
          the standardised datasets to calculate Standardised Severity as an indicator for whether the
          drought is severe or not, rather than for its actual value.
      - Very long droughts exist (i.e. 70 years). These are only recorded in the final period.
        UPDATE THIS FROM THE CATCHMENT LEVEL CODE.
      - Make sure that the river names are being read in without dropping trailing zeros. E.g. 1001.010 != 1001.01
      - Errors common with subtract issue in the return periods. Check cause and fix.
      - Add in check to skip temp_data that has no range in values (i.e. all 0 or all 0.16, for example)
"""

# --- IMPORT PACKAGES ----------------------
from time import sleep
from Hydrological_Flow_and_Drought_Analysis_Functions import *

# --- BEGIN ANALYSIS ---------------------

print("Beginning analysis - if you have an output worksheet open, close it now!")

calculate_flow_stats = True
calculate_return_periods = True
calculate_drought_stats = False # !! DO NOT USE THIS UNTIL YOU HAVE UPDATED FROM THE CATCHMENT LEVEL CODE !!

if not calculate_flow_stats and not calculate_drought_stats and not calculate_return_periods:
    print("Check you are making outputs! 'Flow', 'Return Period' and 'Drought' stats are set to False.")


# --- SET FILE PATHS ----------------------

convex = "I:/SHETRAN_GB_2021/"
analysis_path = convex + "08_Analysis/03 - Flow Analysis/"
warming_levels_path = analysis_path + "Warming_levels_stripped.csv"
cell_lookup = "08_Analysis/02 - UK River Network Creator/UK Catchment Rasters/SHETRAN_UK_River_Network_Autocal_AreaSorted_GT07NSE_Lookup_uniques_with5km.csv"

# Read in warming level dates:
warming_levels = pd.read_csv(warming_levels_path)

# Get a list of the catchments in our network:
master_df = pd.read_csv(convex + cell_lookup, usecols=[0])
master_df['Network_ID'] = master_df['Network_ID'].astype(str)

# Split the ID into its component parts:
master_df['Catchment'] = [x.split(".")[0] for x in master_df['Network_ID']]
master_df['River_Cell'] = [x.split(".")[1] for x in master_df['Network_ID']]

# Add back in any trailing zeros that may have been lost in read/write:
master_df['River_Cell'] = master_df['River_Cell'].str.pad(width=3, side='right', fillchar='0')

# Recreate Network ID as index:
master_df.index = master_df['Catchment'] + "." + master_df['River_Cell']
master_df.drop(columns=['Network_ID'])

# Drop potential duplicates (these should have been dropped at the write stage):
master_df = master_df.drop_duplicates()

catchment_list = master_df["Catchment"].unique().astype("str")

model_tracker = pd.read_csv(convex + "01_Scripts/SHETRAN_UK_Autocal_UKCP18_UDMbaseline/exe_list_all_catchments.csv",
                            index_col=0)

# Set date to be used as a baseline for drought calculations:
drought_baseline_date = "1985-2010"

# --- USER INPUTS ------------------------
# Choose one of the setups to run - also change the tab name below if needed

# --- Set model type:
model = "SHETRAN"  # "SHETRAN" | "HBV"
model_tab_name = 'SHETRAN-UK Autocalibrated'  # 'HBV' | 'SHETRAN-UK Autocalibrated' | 'SHETRAN-UK'

# --- Set model paths:

# # SHETRAN Uncalibrated: (APM runs have some additional parameters to overwrite the default above).
# output_root_name = "01c_UKCP18_APM"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/01c_UKCP18_APM/bc_"
# model_tab_name = "SHETRAN-UK"
# master_folder_historical = convex + "08_Analysis/01 - Collate Flow Datasets/APM_Historical_Outlet_Discharge/"

# SHETRAN Autocalibration Baseline:
output_root_name = "01c_UKCP18_UDMbaseline"
master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/01c_UKCP18rcm_Autocal_UDM_Baseline/bcm_"

# # SHETRAN Calibrated UKCP18 NFM Max (02c):
# output_root_name = "02c_UKCP18_UDMbaseline_NFMmax"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/02c_UKCP18_Autocal_UDM_baseline_NFMmax/bcm_"

# # SHETRAN Calibrated UKCP18 NFM Max STORAGE (02c):
# output_root_name = "02c_UKCP18_UDMbaseline_NFMmax_storage"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/02c_UKCP18_Autocal_UDM_baseline_NFMmax_storage/bcm_"

# # SHETRAN Calibrated UKCP18 NFM Max WOODLAND (02c):
# output_root_name = "02c_UKCP18_UDMbaseline_NFMmax_woodland"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/02c_UKCP18_Autocal_UDM_baseline_NFMmax_woodland/bcm_"

# # Calibrated UKCP18 NFM Max (03 SSP2 2050):
# output_root_name = "03d_UKCP18_UDM_ssp2_2050"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/03d_UKCP18_Autocal_UDM_ssp2_2050/bcm_"

# # Calibrated UKCP18 NFM Max (03 SSP2 2080):
# output_root_name = "03d_UKCP18_UDM_ssp2_2080"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/03d_UKCP18_Autocal_UDM_ssp2_2080/bcm_"

# # Calibrated UKCP18 NFM Max (03 SSP4 2050):
# output_root_name = "03d_UKCP18_UDM_ssp4_2050"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/03d_UKCP18_Autocal_UDM_ssp4_2050/bcm_"

# # Calibrated UKCP18 NFM Max (03 SSP4 2080):
# output_root_name = "03d_UKCP18_UDM_ssp4_2080"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/03d_UKCP18_Autocal_UDM_ssp4_2080/bcm_"

# SHETRAN Calibrated UKCP18 NFM Bal (06c):
# output_root_name = "06c_UKCP18_UDMbaseline_NFMbal"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/06c_UKCP18_Autocal_UDM_baseline_NFMbal/bcm_"

# # SHETRAN Calibrated UKCP18 NFM Bal STORAGE (06c):
# output_root_name = "06c_UKCP18_UDMbaseline_NFMbal_storage"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/06c_UKCP18_Autocal_UDM_baseline_NFMbal_storage/bcm_"

# # SHETRAN Calibrated UKCP18 NFM Bal WOODLAND (06c):
# output_root_name = "06c_UKCP18_UDMbaseline_NFMbal_woodland"
# master_folder_UKCP18 = convex + "05_Climate_Change_Simulations/06c_UKCP18_Autocal_UDM_baseline_NFMbal_woodland/bcm_"


# --- END USER INPUTS --------------------

# Print the name of the output and path as a final check for the user
print(output_root_name)
print(master_folder_UKCP18)
# sleep(2)

# --- TEST ---
# catchment_list = catchment_list[0:3]
# catchment_list = ["29009"]
# --- END ---


# --- CALCULATE HISTORICAL STATISTICS -----
if calculate_flow_stats:
    # Extract flow stats from the historical simulations:
    #   Historical simulations run from 01/01/1980 to 01/01/2011.
    #   We will cut off the first 5 years of the simulation.
    master_df[["hist_q99", "hist_q95", "hist_q05", "hist_q01"]] = pd.NA

    counter = 0
    for catchment in catchment_list:

        counter += 1

        print(f"- {catchment} ({counter}/{len(catchment_list)})")

        try:  # Try/Exception used to account for missing files.

            path = find_historical_simulation_path(catchment_name=catchment, catchment_tracker=model_tracker)
            path = convex + path + catchment + "/output_" + catchment + "_shegraph.h5"

            with h5py.File(path, 'r', driver='core') as hf:
                flows = hf["VARIABLES"]['  4 ovr_flow']['value'][:]

            # Check that the simulation completed (within 10%), else pass:
            if flows.shape[2] < (11324 * 0.9):
                continue

            river_ids = master_df[master_df["Catchment"] == catchment].index
            river_cells = [int(x) - 1 for x in master_df[master_df["Catchment"] == catchment]["River_Cell"]]

            for cell in range(len(river_ids)):
                # river_cell = river_cells.values[cell]-1
                river_cell = river_cells[cell]
                river_id = river_ids[cell]

                # Get the flow direction: (0=north, 1=east, 2=south, 3=west)
                direction = np.argmax(abs(np.sum(flows[river_cell, :, 0:1000], axis=1)))

                # Calculate flow quantiles for the historical simulation:
                master_df.loc[river_id, ["hist_q99"]] = form(
                    np.quantile(flows[river_cell, direction, 365 * 5:], 0.01))  # Low flow
                master_df.loc[river_id, ["hist_q95"]] = form(np.quantile(flows[river_cell, direction, 365 * 5:], 0.05))
                master_df.loc[river_id, ["hist_q01"]] = form(np.quantile(flows[river_cell, direction, 365 * 5:], 0.99))
                master_df.loc[river_id, ["hist_q05"]] = form(
                    np.quantile(flows[river_cell, direction, 365 * 5:], 0.95))  # High flow

        except Exception as e:
            print("EXCEPTION - Network ID: ", catchment, ":")
            print(e)
            continue


# --- SETUP PERIODS & STATISTICS ----------

rcm_list = ["01", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "15"]

# period_list = ["1985-2010",  "1985-2080", # Baseline periods "1980-2000", "1980-2010", "1985-2000", "1985-2015", "1990-2010",
#                "2010-2040", "2020-2050", "2030-2060", "2040-2070", "2050-2080",  # Future periods
#                "WL1.5", "WL2.0", "WL2.5", "WL3.0", "WL3.5", "WL4.0"]  # Warming periods - these will need looking up.

date_indexes = {
    # Dates start 01/12/1980. There are 360 days in a climate year.
    # "1980-2000": [0, 360 * 20],
    # "1980-2010": [0, 360 * 30],
    "1985-2000": [360 * 5, 360 * 20],
    "1985-2010": [360 * 5, 360 * 30],
    # "1985-2015": [360 * 5, 360 * 35],
    # "1990-2010": [360 * 10, 360 * 30],
    "1985-2080": [360 * 5, 360 * 100],

    "2010-2040": [360 * 30, 360 * 60],
    "2020-2050": [360 * 40, 360 * 70],
    "2030-2060": [360 * 50, 360 * 80],
    "2040-2070": [360 * 60, 360 * 90],
    "2050-2080": [360 * 70, 360 * 100],

    # Listed in order of RCP warming period start years.
    # The code reads from the start of the listed year.
    "WL1.5": [2006, 2003, 2007, 2005, 2005, 2006, 2004, 2008, 2004, 2010, 2005, 2006],
    "WL2.0": [2016, 2013, 2018, 2016, 2017, 2018, 2014, 2018, 2015, 2020, 2016, 2019],
    "WL2.5": [2026, 2023, 2028, 2025, 2027, 2029, 2023, 2027, 2025, 2030, 2026, 2030],
    "WL3.0": [2034, 2031, 2037, 2034, 2036, 2038, 2030, 2036, 2034, 2038, 2035, 2038],
    "WL3.5": [2042, 2039, 2044, 2042, 2043, 2047, 2037, 2045, 2042, 2045, 2043, 2046],
    "WL4.0": [2049, 2046, 2051, 2049, 2050, 2055, 2044, 2052, 2050, 2052, 2050, 2054]

}

# Create a list of drought periods (as these won't use all the baseline periods:
drought_periods = list(date_indexes.keys())  # [list(date_indexes.keys())[x] for x in range(len(date_indexes.keys())) if x in [3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]

# --- CREATE BLANK OUTPUTS ----------------

output_list = []
output_names = []

tuples = [(r, p) for r in rcm_list for p in date_indexes.keys()]
output_template = pd.DataFrame(columns=tuples, index=master_df.index)
output_template.index.name = 'Network_id'
output_template.columns = pd.MultiIndex.from_tuples(tuples)
# df = df.sort_index(1)

if calculate_flow_stats:
    output_Q99 = copy.deepcopy(output_template)
    output_Q95 = copy.deepcopy(output_template)
    output_Q50 = copy.deepcopy(output_template)
    output_Q05 = copy.deepcopy(output_template)
    output_Q01 = copy.deepcopy(output_template)
    output_LTQ95 = copy.deepcopy(output_template)
    output_LTQ99 = copy.deepcopy(output_template)
    output_GTQ05 = copy.deepcopy(output_template)
    output_GTQ01 = copy.deepcopy(output_template)
    # output_GTbankfull = copy.deepcopy(output_template)

    # Add outputs to a list for writing:
    output_list.extend([output_Q99, output_Q95, output_Q50, output_Q05, output_Q01,
                        output_LTQ95, output_LTQ99, output_GTQ05, output_GTQ01])  # output_GTbankfull
    output_names.extend(["Q99", "Q95", "Q50", "Q05", "Q01", "LTQ95", "LTQ99", "GTQ05", "GTQ01"])

if calculate_return_periods:
    output_ReturnPeriod_2yr = copy.deepcopy(output_template)
    output_ReturnPeriod_3yr = copy.deepcopy(output_template)
    output_ReturnPeriod_5yr = copy.deepcopy(output_template)
    output_ReturnPeriod_10yr = copy.deepcopy(output_template)
    output_ReturnPeriod_25yr = copy.deepcopy(output_template)
    output_ReturnPeriod_50yr = copy.deepcopy(output_template)
    output_ReturnPeriod_100yr = copy.deepcopy(output_template)

    # Add outputs to a list for writing:
    output_list.extend([output_ReturnPeriod_2yr, output_ReturnPeriod_3yr, output_ReturnPeriod_5yr, output_ReturnPeriod_10yr,
                        output_ReturnPeriod_25yr, output_ReturnPeriod_50yr, output_ReturnPeriod_100yr])
    output_names.extend(["ReturnPeriod_3yr", "ReturnPeriod_5yr", "ReturnPeriod_10yr",
                         "ReturnPeriod_25yr", "ReturnPeriod_50yr", "ReturnPeriod_100yr"])

if calculate_drought_stats:
    # Using periods of interests to droughts, calculate standardised metrics of:
    dps = [x for x in range(len(output_template.columns)) if output_template.columns[x][1] in drought_periods]

    output_drought_duration_mean = copy.deepcopy(output_template.iloc[:, dps])  # (not affected by standardisation)
    output_drought_months = copy.deepcopy(output_template.iloc[:, dps])  # (not affected by standardisation)

    output_deficit_max = copy.deepcopy(output_template.iloc[:, dps])
    output_deficit_mean = copy.deepcopy(output_template.iloc[:, dps])
    output_deficit_total = copy.deepcopy(output_template.iloc[:, dps])

    # Calculate the same [standardised] metrics for only the moderate and major droughts:
    output_drought_duration_mean_severe = copy.deepcopy(output_template.iloc[:, dps])
    output_drought_months_severe = copy.deepcopy(output_template.iloc[:, dps])
    output_deficit_mean_severe = copy.deepcopy(output_template.iloc[:, dps])

    # Add outputs to a list for writing:
    output_list.extend([output_drought_duration_mean, output_drought_months, output_drought_months_severe,
                        output_deficit_max, output_deficit_mean, output_deficit_total,
                        output_drought_duration_mean_severe, output_deficit_mean_severe])
    output_names.extend(["drought_duration_mean", "drought_months", "drought_months_severe",
                         "drought_deficit_max", "drought_deficit_mean", "drought_deficit_total",
                         "drought_duration_mean_severe", "drought_deficit_mean_severe"])


# --- CALCULATE FLOW STATISTICS -----------

print("Calculating statistics for catchments:")
test_time = time.time()
# # Create counter for tracking progress:
counter = 0

# Run through each of the catchments that we intended to model:
for catchment in catchment_list:

    counter += 1

    print(f"- {catchment} ({counter}/{len(catchment_list)})")

    # # Update tracker and print the counter:
    # counter += 1
    # if counter % 100 == 0:
    #     print("--- ", counter, "/698 catchments processed.")

    # Run through each RCM run:
    print("   rcm:")

    for r in range(len(rcm_list)):

        rcm = rcm_list[r]

        print("   - ", rcm)

        # Try to open the flow output:
        try:
            flow_path = os.path.join(master_folder_UKCP18 + rcm, str(catchment),
                                     "output_" + str(catchment) + "_shegraph.h5")

            if os.path.exists(flow_path):
                with h5py.File(flow_path, 'r', driver='core') as hf:
                    f_keys = hf["VARIABLES"].keys()
                    f_key = [k for k in f_keys if 'ovr_flow' in k]
                    flows = hf["VARIABLES"][f_key[0]]['value'][:]


                # Check that the simulation completed 100 years, else skip calculations:
                if flows.shape[2] < 36000:
                    print("Catchment ", catchment, " skipped as incomplete.")
                    continue

                # Sometimes the model outputs are 100yrs x 365 days instead of 100x360.
                # This end period has no driving data, so should be trimmed off.
                flows = flows[:, :, 0:min(36000, flows.shape[2])]

            else:
                continue

        except Exception as e:
            print("Exception - Catchment: ", catchment, ":")
            print("... ", e)
            continue

        river_ids = master_df[master_df["Catchment"] == catchment].index
        river_cells = [int(x) - 1 for x in master_df[master_df["Catchment"] == catchment]["River_Cell"]]

        # Run through all the cells:
        for cell in range(len(river_ids)):
            river_cell = river_cells[cell]
            river_id = river_ids[cell]

            # Get the flow direction:
            direction = np.argmax(abs(np.sum(flows[river_cell, :, 0:1000], axis=1)))
            # Sayers et al. want the return periods to be negative if they flow those directions so make these negative.
            # 0=north, 1=east, 2=south (negative), 3=west (negative)
            sign = -1 if direction in [2,3] else 1

            # ---------------------------------------------------------
            # CALCULATE FLOW QUANTILES AND COUNTS OVER/UNDER THRESHOLD:
            # ---------------------------------------------------------

            flow_df = abs(flows[river_cell, direction, :])

            if calculate_flow_stats or calculate_return_periods:

                # Run through each period:
                for period in date_indexes.keys():

                    # print(r, rcm, catchment, period)

                    # Get the list of indexes/dates from the period dictionary:
                    date_index = date_indexes[period]

                    # If it is a warming period, calculate the correct dates for the period (capped at 2080):
                    if "WL" in period:
                        date_index = np.arange(360 * (date_index[r] - 1980),
                                               min(360 * (date_index[r] - 1980 + 30), 360 * 100))
                    else:
                        # Translate the period string into a list of indexes for the period:
                        date_index = np.arange(date_index[0], date_index[1], 1)

                    temp_data = flow_df[date_index]

                    if calculate_flow_stats:
                        period_years = len(date_index) / 360

                        # Calculate UKCP18 flow quantiles:
                        output_Q99.loc[river_id, (rcm, period)] = form(np.quantile(temp_data, 0.01))  # Very low flow
                        output_Q95.loc[river_id, (rcm, period)] = form(np.quantile(temp_data, 0.05))  # Low flow
                        output_Q50.loc[river_id, (rcm, period)] = form(np.quantile(temp_data, 0.50))  # Median flow
                        output_Q05.loc[river_id, (rcm, period)] = form(np.quantile(temp_data, 0.95))  # High flow
                        output_Q01.loc[river_id, (rcm, period)] = form(np.quantile(temp_data, 0.99))  # Very high flow

                        # Calculate counts under thresholds from HISTORICAL MODEL:
                        output_LTQ99.loc[river_id, (rcm, period)] = form(remove_None(
                            len(temp_data[temp_data < master_df.loc[river_id, 'hist_q99']])) / period_years)
                        output_LTQ95.loc[river_id, (rcm, period)] = form(remove_None(
                            len(temp_data[temp_data < master_df.loc[river_id, 'hist_q95']])) / period_years)

                        # Calculate counts over thresholds from HISTORICAL MODEL:
                        output_GTQ05.loc[river_id, (rcm, period)] = form(remove_None(
                            len(temp_data[temp_data > master_df.loc[river_id, 'hist_q05']])) / period_years)
                        output_GTQ01.loc[river_id, (rcm, period)] = form(remove_None(
                            len(temp_data[temp_data > master_df.loc[river_id, 'hist_q01']])) / period_years)

                        # # Calculate counts under thresholds from OBSERVED DATASET if there is a value:
                        # if not np.isnan(master_df.loc[river_id, 'bankfull_flow']):
                        #     output_GTbankfull.loc[river_id, (rcm, period)] = remove_None(
                        #         len(temp_data.loc[temp_data > master_df.loc[river_id, 'bankfull_flow']])) / period_years

                    if calculate_return_periods:
                        # Calculate return periods UKCP18 Data:
                        try:
                            return_period_years, return_period_flows = calculate_return_events(
                                temp_data, return_periods=[2, 3, 5, 10, 25, 50, 100])
                            output_ReturnPeriod_2yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[0], 2)
                            output_ReturnPeriod_3yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[0], 2)
                            output_ReturnPeriod_5yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[1], 2)
                            output_ReturnPeriod_10yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[2], 2)
                            output_ReturnPeriod_25yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[3], 2)
                            output_ReturnPeriod_50yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[4], 2)
                            output_ReturnPeriod_100yr.loc[river_id, (rcm, period)] = sign*round(return_period_flows[5], 2)
                        except:
                            output_ReturnPeriod_2yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_3yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_5yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_10yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_25yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_50yr.loc[river_id, (rcm, period)] = np.nan
                            output_ReturnPeriod_100yr.loc[river_id, (rcm, period)] = np.nan


            # --------------------
            # CEH Drought metrics:
            # Commented out as this needs updating to fix the issue of overly long droughts extending
            # outside of their period. Update this using the catchment level code.
            # --------------------

            # if calculate_drought_stats:
            #
            #     # >>> STEP 1 & 3 <<<
            #     # (Create long term standardised mean monthly flows)
            #
            #     # --- Aggregate to monthly:
            #     monthly_flow = aggregate_to_monthly(flow_df[:36000])  # The Climate data length
            #
            #     baseline_start = int(date_indexes[drought_baseline_date][0] / 30)
            #     baseline_stop = int(date_indexes[drought_baseline_date][1] / 30)
            #
            #     # Calculate the mean monthly flow (i.e. Jan-Dec) for the baseline period:
            #     mean_monthly_flow_baseline, mean_monthly_flow_baseline_std = mean_baseline_flow(
            #         monthly_flow[baseline_start:baseline_stop])
            #
            #     # Calculate flow anomaly by removing mean monthly baseline flow from the full record:
            #     monthly_flow_anomaly = calculate_flow_anomaly(monthly_flow, mean_monthly_flow_baseline)
            #
            #     # Normalise the anomaly by dividing by the mean month's standard deviation:
            #     monthly_flow_anomaly_normalised = normalise_anomaly(monthly_flow_anomaly,
            #                                                         mean_monthly_flow_baseline_std)
            #
            #     # Create list of flow deficits (i.e. negative normalised anomalies):
            #     monthly_flow_deficit_stnd = [1 if m < 0 else 0 for m in monthly_flow_anomaly_normalised]
            #
            #     # >>> STEP 2 <<<
            #     # (Calculate duration, intensity and severity of deficit of standardised timeseries)
            #
            #     # --- Create data table to hold all the drought data ---
            #
            #     # Start with columns for lengths for droughts and non-droughts:
            #     drought_count = [(i, len(list(g))) for i, g in groupby(monthly_flow_deficit_stnd)]
            #     master_drought_table = pd.DataFrame(drought_count, columns=['drought', 'length'])
            #
            #     # Add a column with indexes of months when each drought/non-drought ends:
            #     master_drought_table["month"] = master_drought_table["length"].cumsum()
            #
            #     # Add columns with indexes for using with Python sub-setting:
            #     master_drought_table["start_index"] = master_drought_table["month"] - master_drought_table["length"]
            #     master_drought_table["end_index"] = master_drought_table["start_index"] + master_drought_table["length"]
            #
            #     # Subset the dataset to only drought periods:
            #     master_drought_table = master_drought_table[master_drought_table["drought"] == 1]
            #     master_drought_table = master_drought_table.reset_index()
            #
            #     # Add columns for intensity and severity:
            #     master_drought_table[
            #         ["intensity_total", "intensity_mean", "severity", "standardised_severity"]] = np.nan
            #
            #     # Run through each period for the catchment and calculate statistics:
            #     for period in drought_periods:
            #
            #         # Get indexes from the date_index dictionary:
            #         date_index = date_indexes[period]
            #
            #         # If it is a warming period, calculate the correct start/end months for the period.
            #         # Capped at 2080, converting from days to months:
            #         if "WL" in period:
            #             date_index = [360 / 30 * (date_index[r] - 1980),
            #                           min(360 / 30 * (date_index[r] - 1980 + 30), 12 * 100)]
            #         else:
            #             # Translate the period string into a start and end month for the period:
            #             date_index = [date_index[0] / 30, date_index[1] / 30]
            #
            #         # IMPORTANT: some of the droughts will cross over between periods. This creates terrible results.
            #         # We need to crop all droughts at their periods, so we will take a subset of the
            #         # data (only containing data for the period), edit the start and end droughts, if needed,
            #         # and then do analysis on that.
            #
            #         # Subset 1. Use filter rows inclusive of those that overlap the thresholds (d_start<p_end + d_end>p_start):
            #         period_drought_table = master_drought_table[
            #             (master_drought_table['start_index'] <= date_index[1]) &
            #             (master_drought_table['end_index'] >= date_index[0])
            #             ].copy()
            #
            #         # Subset 2. Edit the start of the first drought and the end of the last:
            #         period_drought_table.at[period_drought_table.index[0], 'start_index'] = max(
            #             [period_drought_table['start_index'].iloc[0], date_index[0]])
            #         period_drought_table.at[period_drought_table.index[-1], 'end_index'] = min(
            #             [period_drought_table['end_index'].iloc[-1], date_index[1]])
            #
            #         # Subset 3. Calculate new drought durations for the edited rows.
            #         period_drought_table.at[period_drought_table.index[0], 'length'] = \
            #         period_drought_table['end_index'].iloc[0] - period_drought_table['start_index'].iloc[0]
            #         period_drought_table.at[period_drought_table.index[-1], 'length'] = \
            #         period_drought_table['end_index'].iloc[-1] - period_drought_table['start_index'].iloc[-1]
            #
            #         # If step 3 means that there is an initial drought with 0 length, remove this:
            #         period_drought_table = period_drought_table[period_drought_table['length'] != 0]
            #
            #         # --- Calculate the intensities & severities ---
            #
            #         # Run through each drought instance:
            #         for row in period_drought_table.index:
            #
            #             # Create index for monthly flow time series based on the drought period:
            #             # subset the monthly flow time series based on the drought period:
            #             drought_instance = monthly_flow_anomaly_normalised[
            #                                int(period_drought_table.loc[row, "start_index"]):
            #                                int(period_drought_table.loc[row, "end_index"])]
            #
            #             # Calculate intensity (total deficit) and add this to the table:
            #             period_drought_table.loc[row, "intensity_total"] = -drought_instance.sum()
            #
            #             # Calculate mean intensity (average deficit) and add this to the table:
            #             period_drought_table.loc[row, "intensity_mean"] = -drought_instance.mean()
            #
            #             # Calculate Severity (mean intensity x duration):
            #             # Note - I think that this is the same as intensity total, but that that is correct.
            #             period_drought_table.loc[row, "severity"] = period_drought_table.loc[row, "intensity_mean"] * \
            #                                                         period_drought_table.loc[
            #                                                             row, "length"]
            #
            #             # Calculate Standardised Severity:
            #             if period_drought_table.loc[row, "severity"] < 4:
            #                 period_drought_table.loc[row, "standardised_severity"] = 0
            #             if period_drought_table.loc[row, "severity"] >= 4:
            #                 period_drought_table.loc[row, "standardised_severity"] = 1
            #             if period_drought_table.loc[row, "severity"] >= 8:
            #                 period_drought_table.loc[row, "standardised_severity"] = 2
            #
            #         # >>> STEP 4 & 5 <<<
            #         # (Statistics; for droughts and severe droughts [Severity > 4 m3/s])
            #
            #         # --- Calculate Drought Statistics for Periods: ---
            #
            #         # # Run through each period for the catchment and calculate statistics:
            #         period_drought_table_severe = period_drought_table[period_drought_table.standardised_severity > 0]
            #
            #         # Add the duration to the output dataset:
            #         output_drought_duration_mean.loc[catchment, (rcm, period)] = round(
            #             period_drought_table["length"].mean(skipna=True), 3)
            #         output_drought_duration_mean_severe.loc[catchment, (rcm, period)] = round(
            #             period_drought_table_severe["length"].mean(skipna=True), 3)
            #
            #         output_drought_months.loc[catchment, (rcm, period)] = round(
            #             period_drought_table["length"].sum(skipna=True), 3)
            #         output_drought_months_severe.loc[catchment, (rcm, period)] = round(
            #             period_drought_table_severe["length"].sum(skipna=True), 3)
            #
            #         # Add intensity statistics to output dataset:
            #         output_deficit_max.loc[catchment, (rcm, period)] = round(
            #             period_drought_table["intensity_total"].max(skipna=True), 3)
            #         output_deficit_mean.loc[catchment, (rcm, period)] = round(
            #             period_drought_table["intensity_mean"].mean(skipna=True), 3)
            #         output_deficit_total.loc[catchment, (rcm, period)] = round(
            #             period_drought_table["intensity_total"].sum(skipna=True), 3)
            #         output_deficit_mean_severe.loc[catchment, (rcm, period)] = round(
            #             period_drought_table_severe["intensity_mean"].mean(skipna=True), 3)

    # ---------------------------------------------
    # Write partially Completed documents as backup
    # ---------------------------------------------

    # # Write evey 50 catchments:
    # if counter % 50 == 0:
    #     print("Writing PARTIAL Excel documents.")

    #     for i in range(len(output_list)):
    #         output_path = analysis_path + "Outputs/Partial_Backups/Partial_" + \
    #                       output_root_name + "_RiverNet_" + output_names[i] + ".xlsx"
    #         with pd.ExcelWriter(output_path) as writer:
    #             output_list[i].to_excel(writer, sheet_name='SHETRAN-UK Autocalibrated')

print("TIME: ", time.time() - test_time)

# -----------------------------
# WRITE FLOW/DROUGHT STATISTICS
# -----------------------------

print("Writing Excel documents.")

# for i in range(len(output_list)):
#     output_path = analysis_path + "Outputs/" + output_root_name + "_RiverNet_" + output_names[i] + ".xlsx"
#     with pd.ExcelWriter(output_path) as writer:
#         output_list[i].to_excel(writer, sheet_name='SHETRAN-UK Autocalibrated')

for i in range(len(output_list)):
    output_path = f"{analysis_path}Outputs/02_River_Network/{output_root_name}_RiverNet_{output_names[i]}.xlsx"

    # Check whether to append or write new file:
    if os.path.exists(output_path):
        # Append data. This will overwrite sheets with the same name:
        with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
            output_list[i].to_excel(writer, sheet_name=model_tab_name)
    else:
        # Write data to new workbook:
        with pd.ExcelWriter(output_path, mode='w') as writer:
            output_list[i].to_excel(writer, sheet_name=model_tab_name)

