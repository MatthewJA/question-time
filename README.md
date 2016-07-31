# govhack-2016 project - Question Time

GovHack project with @mitchellbusby!

##What is question time?

<p>Love Hansard but wish it was somehow represented on a map? So do we. That's why we created *Question Time*.</p>

<p>We wanted to visualise how political debate occurs over time. For each day of the 2015 – 2016 NSW Parliament, *Question Time* visualises mentions of NSW suburbs found in the NSW Parliament Hansard with a heatmap of how unusually often each suburb was mentioned.</p>

<p>*Question Time* also identifies interesting places for each day Parliament sat. Clicking one of these locations shows a quick snippet of what we think made it interesting.</p>

<p>We mined location data from the NSW Hansard using the <a href="https://www.parliament.nsw.gov.au/hansard/Pages/Hansard-API.aspx">API provided by the Parliament of NSW</a>, and tallied each location mentioned on each day, taking note of where that location was mentioned in the Hansard fragments for later reference. Locations such as Sydney and Newcastle dominated the tallies, so we normalised all tallies by dividing by the average number of mentions per day across the whole 2015 – 2016 period. We then used the tallies to construct and display a heatmap over NSW using the OpenLayers 3 mapping library. For each day, we extracted interesting locations by looking for locations with unusually high numbers of mentions, and again used the NSW Hansard API to extract snippets of text about that location on that day. We then used the <a href="http://www.nltk.org/">NLTK Python library</a> along with github/@aneesha's implementation of the <a href="https://github.com/aneesha/RAKE">RAKE algorithm</a> to highlight key phrases in these snippets and included these alongside the interesting locations to try and explain what made each location interesting. Finally, we built a web app to display the heatmap and interesting locations for each day.</p>
