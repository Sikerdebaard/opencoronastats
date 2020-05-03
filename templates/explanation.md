
[//]: # ([TOC])  
  
# Population

## Top-10 municipality by fastest growth in hospitalized case count

This chart attempts to show a top-10 of municipalities with the fastest raise in hospitalized COVID patients. This data can potentially indicate new localized outbreaks. It shows a cumulative line per municipality that reflects how many hospitalized patients were treated. The data for this chart is taken from [CBS](https://opendata.cbs.nl/statline/#/CBS/nl/dataset/70072NED/table?fromstatweb) directly and [RIVM](https://www.rivm.nl/coronavirus-covid-19) trough [CoronaWatchNL](https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data-geo/data-municipal/RIVM_NL_municipal.csv).

The method used is as follows:

 1. First we take the RIVM reported hospitalized on a municipality level and rebase to 1 in 100 000.
 2. Then we calculate the intra-day percentage change over the values of step 1 to get a growth-factor.
 3. We then take the average of the last three days of growth-factor as calculated by step 2.
 4. Finally we take the RIVM reported hospitalized on a municipality level and sort the municipalities by the calculated growth-factor from step 3 and take the top 10.

[//]: [f1]:http://chart.apis.google.com/chart?cht=tx&chf=bg,s,FFFFFF00&chl=f%28rebased%29%20%3D%20hospitalized_i%20%2F%20municipality%20population%20size%20%2A%20100000
[//]: [f2]:http://chart.apis.google.com/chart?cht=tx&chf=bg,s,FFFFFF00&chl=f%28growth%29%20%3D%20rebased_i%20%2F%20rebased_%7Bi-1%7D%20-%201
[//]: [f3]:http://chart.apis.google.com/chart?cht=tx&chf=bg,s,FFFFFF00&chl=f%28avg%29%3D%5Cfrac%7B%28growth_%7Bi%7D%2Bgrowth_%7Bi-1%7D%2Bgrowth_%7Bi-2%7D%29%7D%7B3%7D
