# Startlists-Qualification-Heats

Target: 
Create balanced qualification heats for orienteering based on World Ranking

Application:
WOC, Worldcup, EOC,....


What are we looking for:    
1. Balance number of runners per heat
2. Balance number of runners from one country per heat.
3. Equal strength of heats.
4. Runners from same country in a heat should not start after each other.
5. Respect startgroup requests.
6. Ensure randomness. 

Solution:
World Ranking is used to rank athletes.   
Rank 1,2,3 are allocated to different heats.  
Repeat for rank 4,5,6,...7,8,9,...  
Google OR Tools solver is used to find solution that meets all constraints.  
Randomness is ensured by fixing random runners to heat 1,2,3.  

Usage:  
Step 1: Update LP_start_entries.xlsx  
It is important that your file looks exactly the same as the example   

Step 2:
For organisers with Python knowledge I would suggest to run the Python script.  
Other organisers can use the exe file. Exe file is not available on Github but can be downloaded from IOF Website.
(https://orienteering.sport/orienteering/internal/event-organising/plan-and-organise-an-iof-event/ )
In both cases the LP_start_entries.xlsx file should be in same directory.

Step 3:
Consult the proposed startlists in startlists.xlsx  
If you would not like the result, just run the program again. ( do not forget to close startlists.xlsx before next attempt) 

Notes: 
* I compiled to *.exe with auto-py-to-exe.  
* Do not hesitate to contact me for support. 
* standard = 3 heats but works also for different number of heats
