[TOC]

# ICU

##   Doubling time / Half life
The doubling time is the time it takes for the population to double in size. In this case it describes the amount of days it takes for the number of COVID patients in the ICU's to double. This calculation assumes that the growth factor is stable, which might not always be the case.

The half life is the time it takes for the population to halve in size. In this case it describes the amount of days it takes for the number of COVID patients in the ICU's to halve. This calculation assumes that the growth factor is stable, which might not always be the case.

## Growth rate
Growth rate describes the growth of new COVID patients in the ICU as a day to day percentage change.

## Patients recovered from ICU
You are looking at a cumulative number of patients that have recovered from the ICU. These patients are no longer in the ICU. Either because they have been moved out or because they are deceased.

## Patients deceased in ICU
This shows the number of COVID patients that have died in the ICU.

## Beds used for COVID / beds used in ICU
The number of ICU beds in use for COVID patients. The card shows an absolute value as reported by the LCPS and is updated daily around 16:00. The chart shows both Stichting-NICE and LCPS reported numbers.

## Case Fatality Rate in ICU
The Case Fatality Rate (CFR) shows the percentage of patients that have died in a group. In this case it describes the percentage of patients that have died in the ICU.

## Growth of confirmed COVID patients in ICU
This chart shows the growth of new COVID patients as a day to day percentage change. A Simple Moving Average is calculated to filter out some signal noise.

## Evolution of mortality rate in ICU
A day to day Case Fatality Rate is calculated, and is displayed in this chart. This allows monitoring when the CFR flattens out. Currently it is expected that the CFR flattens out around 25%-30%.

## Patients recovered vs. deceased
A chart that shows patients recovered vs. deceased. It also shows patients moved from the ICU to the hospital. A weird dip is observed around 2020-04-24. A possible explanation for this could be that patients that have been moved to the hospital are moved back into the ICU.

# Population

## Top-10 municipality by fastest growth in hospitalized case count

This chart attempts to show a top-10 of municipalities with the fastest rise in hospitalized COVID patients. This data can potentially indicate new localized outbreaks. It shows a cumulative line per municipality that reflects how many hospitalized patients were treated. The data for this chart is taken from [CBS](https://opendata.cbs.nl/statline/#/CBS/nl/dataset/70072NED/table?fromstatweb) directly and [RIVM](https://www.rivm.nl/coronavirus-covid-19) trough [CoronaWatchNL](https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-geo/data-municipal/RIVM_NL_municipal.csv).

The method used is as follows:

 1. First we take the RIVM reported hospitalized on a municipality level and rebase to 1 in 100 000.
 2. Then we calculate the intra-day percentage change over the values of step 1 to get a growth-factor.
 3. We then take the average of the last three days of growth-factor as calculated by step 2.
 4. Finally we take the RIVM reported hospitalized on a municipality level and sort the municipalities by the calculated growth-factor from step 3 and take the top 10.
