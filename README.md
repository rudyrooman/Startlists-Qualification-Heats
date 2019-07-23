# Startlists-Qualification-Heats

Target: 
Create balanced qualification heats for orienteering.

Application:
WOC, Worldcup, EOC,....

Requirements:
1. Balance runners per heat
2. Balance runners from one country per heat.
3. Equal strength of heats. 
4. Runners from same country in a heat should not start after each other.
5. Respect as much as possible startgroup requests.
6. Ensure randomness. 

Solution:
World Ranking is used to rank athletes. 
Rank 1,2,3 are allocated to different heats. 
( and this is repeated for rank 4,5,6,...)
Google OR Tools are used to solve.

Usage:
Update entries.xlsx
Run the script
Output: starlists.xlsx
