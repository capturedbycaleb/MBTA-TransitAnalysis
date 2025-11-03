# MBTA-TransitAnalysis
MBTA-TransitAnalysis shows graphs and chars of the Green line B stations going through Boston Massachussets. It shows real time charts and table data with each individual station and wait time statistics. This comes from the MBTA developer website with API keys that gives real time info which is then converted to tables and graphs to allow for easier visualization and comprehension of all the data.

## Features
- All stations and average wait times going toward Boston College and government.
- Name of all green line stations
- Graph with all stations with direction, mean wait time in minutes, median wait time in minutes, and standard deviation wait time in minutes.
- Compares average wait time at each station going inbound and outbound.
- Shows busiest stations on green line B.

## Technology Used
- Python
- API requests
- Numpy / Pandas
- Matplotlib
- MBTA API

## To Run Code
- Press the play button

## Challenges Faced
- Making the code funciton properly all the time.
- Have the graph show all route every single time.

## References
- MBTA line
- MBTA Developer website

## Improvements
- Have the graph work all the times showing every bar rather than some.
- Allow the graphs to load faster.
- Add live data tables of train line B updating in real as you run code.
  
## Patterns and Insights
From the data retrieved by MBTA Green line B, it reveals that the average wait time for passengers heading towards Government Center to be longer than those waiting and traveling towards Boston College. With some stations having different wait times than others. One such instants is a 10.67 minutes median wait time towards Boston College at Babcock street while a 7 minute median wait time towards Government Center. Train wait times also tended to increase in downtown areas such as Park Street where either direction was 11 minutes. This reflects more passangers in those areas waiting for a train. 

This shows that the busiest station is Government center as most people are getting onto or off the train heading towards government Center. This is also because Government center is the last stop before heading towards Boston college which makes it a intersection point. Government center is also a civic district rather than residential area so more people woould be waiting in order to go home.

In all other areas of the green line however, the median wait time was 10 minutess suggesting that the trains are consitent with travel between station to station. This signifies that overall, the MBTA green line is consistent and that it has larger service in the downtown region of Boston.

## Author
- Edwin Huang, Caleb, Cyrus
