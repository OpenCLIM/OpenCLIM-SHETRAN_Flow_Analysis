# README - Hydrological Flow and Drought Analysis
Newcastle University

Ben Smith

26/10/2022

## Summary

These scripts and results analyse flow timeseries for the UK for future UKCP18 climate scenarios. Outputs are taken from hydrological models: SHETRAN (Newcastle University) and HBV (University of East Anglia). Two lines of analysis are taken: flow analysis, looking at flow quantiles and peaks over/under thresholds; and drought analysis, following the methods of CEH as in Rudd et. al (2017 & 2019). Drought metrics produced here are roughly equivalent to those produced by CEH in the referenced papers, but are presented for catchments, rather than regionally.

All statistics are calculated from hydrological models that are benchmarked against recorded historical flows and driven by bias controlled UKCP18 climate data for all 12 RCPs. All simulations run for 100 years from 1980-2080.

These statistics should not be used in instances where the underlying models have poor performance (i.e. NSE values <0.5). NSE values of <0.7 could also be avoided if only the 'best' models are desired.

## Time Periods

Metrics for flow analysis are calculated for the following baseline periods to assess the impact of model spinup and choice of baseline:
- 1980-2000
- 1980-2010
- 1985-2000
- 1985-2010
- 1985-2015
- 1990-2010

Metrics for drought analysis (using the CEH methods) are calculated using a single baseline of 1985-2010. This should also be the default baseline period for comparisons for the flow metrics. Metrics were also produced for the following future periods:
- 2010-2040
- 2020-2050
- 2030-2060
- 2040-2070
- 2050-2080
- WL1.5
- WL2.0
- WL2.5
- WL3.0
- WL3.5
- WL4.0

'WL' represents warming levels, when the average tempterature rises by x degrees C above the baseline. Model 'spin up' refers to a period at the start of the hydrological model where it sets up; during this period modelled flows are less accurate.


## Flow Analysis

The following metrics are calculated:
- Q99: Very high flows
- Q95: High flows 
- Q50: Median flows
- Q05: Low flows
- Q01: Very low flows
- LTQ95: Counts of flows under low flow threshold
- LTQ99:  Counts of flows under very low flow threshold
- GTQ05:  Counts of flows over high flow threshold
- GTQ01:  Counts of flows over very high flow threshold
- GTbankfull: Counts of flows over the recorded bank-full threshold (NRFA)

All thresholds are taken from the historical model (1985-2010, 1980-85 spinup period removed). This means that the % of the flow timeseries  that is under/over threshold for quantiles in the default baseline period (1985-2010) will not equal the quantile.

## Drought Analysis

Three metrics were calculated based on the full drought catalogue:
- Mean Drought Duration: the length of time in flow deficit (months);
- Drought months: the number of months of drought in the period (months);
- Mean Drought Deficit: i.e. intensity (m3s-1);
- Max Drought Deficit: i.e. intensity (m3s-1);
- Total Drought Deficit: i.e. intensity (m3s-1);

An additional metric was calculated using only severe droughts:
- Mean Severe Drought Deficit: i.e. intensity (m3s-1);
- Severe Drought Months: the number of months of severe drought in the period (months);
- Mean Severe Drought Deficit: i.e. intensity (m3s-1);

All metrics are for standardised flows to allow for comparisons between catchments; see below for method.

The following metrics are not included:
- Drought severity — duration multiplied by mean standardised drought intensity (standardised deficit).

The method matches that of the eFLaG project, as was used for MaRIUS. I.e. droughts are identified using the threshold level method (Yevjevich, 1967; Hisdal et al. 2004) with the standardisation method previously developed by Rudd et al. (2017) for use with Grid2Grid model output. They applied the procedure summarised below to time-series of G2G-simulated monthly mean river flow to identify droughts, and their characteristics. 

The drought identification and characterisation procedure is as follows: A drought event is assumed to start when the river flow falls below a threshold, and continues until the threshold is exceeded again. Here the threshold is the long-term mean monthly flow from December 1985 - November 2010 (i.e. baseline period), thus removing the seasonality in hydrological response.

The procedure is as follows:
1. Remove the long-term monthly mean flow, Xmon (1989-2018) from the monthly mean time series, X.
anomaly = X - Xmon
2. Divide by the long-term monthly standard deviation for the baseline period to standardise the anomaly: Standardised anomaly = (X - Xmon)/σmon

Dividing by the standard deviation of mean monthly flow, σmon, allows for the comparison of drought characteristics for different locations (Peters et al. 2003). Thus a “drought” is defined as the period of time for which the variable is below normal, i.e. a deficit.

3. Where the anomaly is negative (i.e. a deficit) calculate the duration, intensity and severity of that deficit.

4. Select only the deficits where the standardised severity is greater than or equal to the severity thresholds in Table 1 (severity thresholds used in Rudd et al 2017 and 2019).

Severity thresholds:
- Moderate-threshold: 4 cummecs
- Major-threshold: 8 cummecs

References:
- Rudd, A.C., Kay, A.L. and Bell, V.A. (2019). National-scale analysis of future river flow and soil moisture droughts: potential changes in drought characteristics. Climatic Change. doi: 10.1007/s10584-019-02528-0
- Rudd, A.C. Bell, V.A., Kay, A.L. (2017) National-scale analysis of simulated hydrological droughts (1891-2015) Journal of Hydrology 550, 368-385 doi:10.1016/j.jhydrol.2017.05.018