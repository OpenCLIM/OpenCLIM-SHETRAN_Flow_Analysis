# Statistics and Metric Calculation Steps
## Droughts
**Drought statistics were calculated to allow for comparison with other projects and, as such, followed the method of drought extraction used in the comparable eFLaG project (Hannaford et al, 2023). Analysis therefore follows the methodology of Rudd et al. (2017, 2019), where droughts are identified using a threshold level method (Yevjevich, 1967; Hisdal et al., 2004; Fleig et al., 2006) coupled with a standardisation method (Peters et al., 2003).** 

This procedure, summarised below, is applied to time-series of simulated daily river flow that has been aggregated into monthly flow data by taking the mean of the daily flow.

### Identifying and Classifying Droughts
A drought event is assumed to start when the river flow falls below a threshold and continues until the threshold is exceeded again. This threshold is the long-term monthly mean flow from December 1985 – Dec 2010 (the baseline period of each RCM). To remove seasonality from the hydrological response, long-term mean monthly flows are calculated (i.e. the mean flow for each of the 12 months for the 25-year baseline period) and then deducted from the monthly flows. The result of this is the monthly flow anomaly, where negative flows, or flow deficits, are indicative of a drought. To allow comparison of drought characteristics for different catchments, the time series of monthly flow anomalies can be standardised (Peters et al., 2003) by dividing it by the standard deviation of mean monthly flow.

As such, for each simulation output, the following calculations are performed:
1. 	Aggregate the daily flow output into monthly flow.
2. 	Calculate the long-term monthly mean flows (1985-2010) (i.e. mean flow for each of the 12 months over the period).
3. 	Deduct the long-term monthly mean flows from the monthly flow to calculate the monthly flow anomaly.
4. 	Normalise the monthly flow anomaly by dividing all values by the standard deviation of long-term monthly mean flows for their respective months to calculate the normalised monthly flow anomaly.

A further statistic can be calculated that considers only the more extreme droughts by applying a severity index. In this instance, the drought instances can be attributed a severity according to deficit severity thresholds (Rudd et al., 2017, Rudd et al., 2019). For severe statistics used in this work, only moderate and major droughts are considered. To calculate the drought severities:

5. 	Where the normalised monthly flow anomaly is negative, calculate the total flow deficit for that each drought instance.
6. 	Assign a drought severity to each drought instance according to the following thresholds of total flow deficit:
- Minor: 0-4m3/s
- Moderate: 4-8 m3/s
- Major: ≥8 m3/s

### Drought Metrics
- Drought Months [Severe] (months): a count of months with negative normalised monthly flow anomalies within the period.
- Drought Duration [Severe] (months): the mean length of the drought instances within the period. In instances where the whole period is classified as being in drought, the drought duration will be limited by the length of the period, which, in some instances, may be shorter than 30 years, e.g. if the warming period (Tab. B1) continues beyond the end of the dataset in 2080.
- Drought Deficit [total, mean, mean severe, max] (m3/s): the sum, mean, and maximum of the normalised monthly flow anomaly of each drought instance, also known as drought standardised drought severity (e.g. Rudd et al, 2017). As all metrics are standardised for inter-catchment comparison, these drought deficits are much smaller than if they were calculated directly from unstandardised flows. 
- [Severe] metrics: these are calculated in the same way as above, but using only those drought instances that have moderate or major severities.
- Short periods: Some periods are shorter than the standard 30 years, (e.g. the baseline periods and those warming periods that continue beyond the end of the dataset in 2080, see Tab B1). For these periods, drought deficits and counts of drought months have been normalised to a 30-year period.

## Return Periods Metrics
Return periods were calculated for each catchment by taking the maximum annual daily flow for each year (1st December to 30th November) and fitting shape, loc, and scale parameters to their distribution using lmoments (Python Package Lmoments3). Parameters were then fitted to a general extreme value distribution (using the ScyPy Python package) to allow the extraction of return period flows. Return periods were calculated for 2, 3, 5, and 10-year return periods. Higher return periods (e.g. 25, 50 and 100-year events) can be calculated, but, as these become less statistically robust as the period increases, due to the need for longer and longer input timeseries, these are not presented in this work.

## Flow Quantiles and Peaks Over Threshold (POT)
Flow quantiles were calculated for each catchment by taking the period of data and simple taking the desired quantile. The quantile (QX) describes the flow value which is exceeded X% of the time, with Q95 and Q99 describing low and very low flows, Q5 and Q1 describing high and very high flows, and Q50 describing median flows. 

Annual Peaks Over Threshold (POT) were calculated by counting the number of daily instances that the flow exceeded historical flow quantiles. So, for example, the GTQ5 statistic counts the number of days when the flow exceeded the historical Q5 quantile. The LTQ95 statistic counts the number of days when the flow was lower than the historical Q95 quantile. The historical quantiles are taken from the autocalibrated historical model (Sec. 2.2), from the period 1985-2010. As the counts of POT in the baseline climate simulations will differ from the counts of POT in the historical runs, all future climate statistics should be compared to the baseline, not directly to the historical data. All counts are given per year, to enable comparisons with values calculated over shorter periods (e.g. for 4°C of warming, where the period sometimes goes beyond the end of the dataset).
