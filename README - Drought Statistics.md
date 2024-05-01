# Drought Statistics

Ben Smith

25/10/2023

## Background
*[As summerised from A. Rudd, CEH, 27/07/2022]*

Statistics were calculated to follow the analysis done at CEH for the BEIS project. This followed the same method of drought extraction for eFLaG as was used for MaRIUS, i.e. Droughts are identified using the threshold level method (Yevjevich, 1967; Hisdal et al. 2004) with the standardisation method previously developed by Rudd et al. (2017) for use with G2G model output. This procedure, summarised below, is applied to time-series of simulated daily (aggregated to monthly) mean river flow to identify droughts, and their characteristics.  

The drought identification and characterisation procedure is as follows: 
- A drought event is assumed to start when the river flow falls below a threshold, and continues until the threshold is exceeded again. Here the threshold is the long-term mean monthly flow from December 1980 - Dec 2010 (i.e. baseline period), thus removing the seasonality in hydrological response.

- Step 1: Remove the long-term monthly mean flow, Xmon (1980-2010) from the monthly mean time series, X. anomaly = X - Xmon 

- Step 2: Where the anomaly is negative (i.e. a deficit) calculate the duration, intensity and severity of that deficit.  
    i. drought intensity: the deficit (m3s-1); 

    ii. drought duration: the length of time in deficit (months); and 
    
    iii. drought severity: duration multiplied by mean drought intensity.

To allow comparison of drought characteristics for different locations the time series of flow “anomalies” can be standardised (Peters et al. 2003) by dividing by the standard deviation of mean monthly flow, σmon, also from the years 1989-2018. Thus a “drought” is defined as the period of time for which the variable is below normal, i.e. a deficit.

- Step 3: Repeat steps 1 and 2 for the standardised anomaly by dividing by the long-term monthly standard deviation (1989-2018) 
standardised anomaly = (X - Xmon)/σmon 

- Step 4: Select only the deficits where the standardised severity is greater than or equal to the severity thresholds in Table 1 (severity thresholds used in Rudd et al 2017 and 2019). 
    
    iv. Standardised drought severity: duration multiplied by mean standardised drought intensity (standardised deficit).  

Rudd, A.C., Kay, A.L. and Bell, V.A. (2019). National-scale analysis of future river flow and soil moisture droughts: potential changes in drought characteristics. Climatic Change. doi: 10.1007/s10584-019-02528-0
Rudd, A.C. Bell, V.A., Kay, A.L. (2017) National-scale analysis of simulated hydrological droughts (1891-2015) Journal of Hydrology 550, 368-385 doi:10.1016/j.jhydrol.2017.05.018


## Statistics

**Drought Duration:** The mean lengths of droughts in the period (months). 

**Drought Months:** The number of months classified as being in drought in the period.

**Drought Deficit:** The maximum/mean/total volume of water under the mean monthly flow in the drought period. I.e. the amount of water (in cumecs) that would be required to restore flow to the monthly mean.


## Calculation Steps

### Data Preperation 
1. All calculations are performed using monthly data, created by taking the 30 day means. 
2. Monthly flow anomolies are then calculated my calculating the mean flow for each month (i.e. the mean flow in all Januarys) during the baseline period and then deducting these values from each month across the time series.
3. The flow anomolies are then normalised by dividing the anomoly by each month's standard deviation.
4. *Drought Intensity* total and mean are calculated by summing and averaging the drought anomoly for each drought period (i.e. each month or consecutive group of months with negative anomolies).
5. *Drought Severity* is calculated for each drought period by multiplying its mean intensity by its length. (This is the same as the total intensity). 
6. The *Standardised Drought Severity* is calculated for each drought period, with standarised severities >=8 considered severe. Standardised severity was calculated using the following thresholds:
    - Severity of 0 to 4 cumecs = standardised severity of 0.
    - Severity of 4 to 8 cumecs= standardised severity of 1 (moderate).
    - Severity >=8 cumecs = standardised severity of 2 (major).


### Drought Duration 
Calculated by taking the mean length of all droughts (i.e. negative anomolies) within the period of interest. *Severe drought durations* are calculated in the same way using only those drought instances that count as severe.

### Drought Months
*Drought months* is a simple count of those months with negative drought annomolues within the period. Severe drought durations are calculated in the same way using only those drought instances that count as severe.

### Drought Deficit
This is the similar to the drought intensity.
- *Max deficit* is gretest total intensity over the period, i.e. the greatest drought anomoly.  
- *Mean deficit* takes the mean of the mean drought intensities. (Severe)
- *Sever Mean deficit* is calculated as above, but only using those drought instances that were classed as 'severe'.
- *Total drought deficit* was calculated by summing the mean intensity from the different dought instances. **I am not sure that this is a useful statistic. It should be removed or corrected, as I think it should use the total of totals, not the total of means.**