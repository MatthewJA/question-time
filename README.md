# govhack-2016 project - Question Time

GovHack project with @mitchellbusby!

##What is question time?

Love Hansard but wish it was somehow represented on a map? So do we. That's why we created *Question Time*.

We love political banter, and we wanted to visualise how political debate occurs over time. For each day of the 2015 -- 2016 NSW Parliament, *Question Time* visualises mentions of NSW suburbs found in the NSW Parliament Hansard with a heatmap of how unusually often each suburb was mentioned.

We also analyse the top five location mentions in NSW on each sitting day and plot them on the same map. Clicking one of these locations opens data in the sidebar about why it was interesting on that day. We're going to start out with snippets of mentions in Hansard, but plan to include more interesting record information via NLP.

We made extensive use of Python's Flask and also the OpenLayers 3 mapping library that gives us heatmaps overlaid onto regular maps for free.