# Startlists-Qualification-Heats
Feel free to contact me via email( in .py file ) for support 

Target: 
Create balanced qualification heats for orienteering.

Application:
WOC, Worldcup, EOC,....

Requirements:
1. Balance runners per heat
2. Balance runners from one country per heat.
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
Update entries.xlsx
Run the script
Output: startlists.xlsx

For organisers: compile to *.exe with Pyinstaller.
