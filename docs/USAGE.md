# Making the Most of Your Scrim Data

So you've captured your scrim data - now what? 

The key is to treat your data as a crucial input into your larger coaching strategy, not just numbers on a spreadsheet. Integrating data capture and analysis into your Valorant practice routine can give you a significant competitive advantage. By consistently capturing data with tools like Practistics, digging into that data to find insights, and using those insights to inform your training and strategy, you can pinpoint your team's areas for improvement and track your progress over time. Data-driven coaching takes work to set up and maintain, but the payoff is well worth it. With the right analytical approach, you can take your team's performance to the next level.

## What You Can Track

Think of your scrim data as a story waiting to be told. Each round captures:
- Who got first blood (and how early)
- Which sites you're playing
- Was it a post-plant?
- How your economy decisions play out
- Complete round timelines with every kill, plant, and defuse
- Was it a 5v4, 4v5, true first-blood round, or traded, and much more.

Look at the [data points documentation](/DATA_STRUCTURE.md) for more details.

## Data to Capture

Practistics records a wealth of data from each scrim. Some of the most important data points to pay attention to include:

- **First Bloods**: Which players/agents are getting the most first kills? On which parts of the map are they getting them? How much impact do first bloods have on round win rate?

- **Site Hit Rates**: What percentage of your attacking rounds are spent hitting each site? What is your success rate on each site? 

- **Plant Locations**: Where are you planting the spike most often on each map? Are certain plant spots more effective than others?

- **Retake Success**: When you lose the site on defense, how often are you able to retake and defuse? Which retake strategies are most successful?

- **Agent-Specific Stats**: For each agent, track key metrics like kill/death ratio, first blood rate, clutch success rate, etc. This can help optimize your team composition.

- **Economy Trends**: How does your win rate differ on full buy rounds vs. eco rounds? What is the impact of getting a plant on your economy? 

- **Ult Usage**: How often is each ult being used? What is the win rate for rounds where each ult is used?

Collecting this data over a large number of scrims will give you a robust dataset to work with.

## Analysis Techniques

There are many ways to slice and analyze your Practistics data. Some common techniques include:

- **Descriptive Statistics**: Use summary stats like means, medians, and percentages to get a high-level view of your team's performance. For example, what is your average win rate on attack vs. defense?

- **Trend Analysis**: Plot your key metrics over time to spot trends. Is your retake success rate improving from week to week? 

- **Correlation Analysis**: Look for relationships between different variables. Does getting first blood correlate with winning the round? Does a higher ult usage rate correlate with a better win rate?

- **Heat Maps**: Create visual heat maps of the most common areas for kills, deaths, plants, etc. on each map. This can reveal problematic spots or effective strategies.

- **Player Performance**: Calculate advanced stats for each player like KAST (Kills, Assists, Survived, Traded), ADR (Average Damage per Round), KPR (Kills Per Round), etc. Use these to quantify each player's impact.

To do this analysis, you can use tools like:

- **Excel/Google Sheets:** Quick and easy for basic analysis. Great for calculating things like kill/death ratios, win rates, etc.
- **Tableau:** Powerful data visualization tool. You can create interactive dashboards to view trends over time.
- **R/Python: **If you want to do more complex statistical analysis, these programming languages are a great choice. You could build predictive models to figure out your optimal team comps, for example.
- **PowerBI:** Business intelligence tool that's great for building shareable dashboards. Nice balance of analysis and visualization capabilities.


## Integrating Data into Coaching

The true power of data analysis comes from using it to directly inform your team's practice and strategy. Here's how you might integrate Practistics into your coaching workflow:

1. **Set Data-Driven Goals**: Use your data to identify specific, measurable areas for improvement. For example, "Increase our defensive win rate on Haven from 45% to 55% over the next month." 

2. **Design Focused Drills**: Create practice drills that target your areas of weakness. If your data shows you struggle to hold B site on Ascent, drill your B site setups and retake strategies.

3. **Track Individual Progress**: Use player-specific stats to set individual performance goals and track progress over time. If your Jett has a low first blood rate, work with them on their entry techniques and movement.  

4. **Inform Agent Selection**: Use your agent-specific performance data to optimize your team comp. If your Sova is consistently outperforming your Breach, maybe it's time for a role swap.

5. **Review in VOD Sessions**: Incorporate data into your VOD review sessions. If you notice a trend in the data, pull up specific round examples to see what's happening in the server.

