SCREENER:

https://elite.finviz.com/screener.ashx?v=111\&s=ta\_toplosers\&f=exch\_nyse,geo\_usa,idx\_sp500,sh\_avgvol\_o1000,sh\_float\_o50p,sh\_opt\_option,sh\_price\_u3,sh\_relvol\_o2,sh\_short\_high,targetprice\_b20\&o=-\&ar=10

=======================================

AUTH TOKEN:



YOUR TOKEN GOES HERE



EXAMPLE EXPORT API URL:



https://elite.finviz.com/export.ashx?v=111\&f=fa\_div\_pos,sec\_technology\&auth=28e8cc3f-ad7c-480f-98e9-5c9860de79d7



=======================================
Set up your filters in the main Screener interface

Open Screener
2
Replace URL Path

Change "screener.ashx" to "export.ashx" in your URL

Screener URL

https://elite.finviz.com/screener.ashx?v=111\&f=fa\_div\_pos,sec\_technology
Screener Export URL

https://elite.finviz.com/export.ashx?v=111\&f=fa\_div\_pos,sec\_technology
3
Customize Columns Optional

Specify which columns to export using the "\&c=column1,column2" parameters



Learn More
4
Add Authentication

Append your API token to the URL







Regenerate Token

Example Export API URL

https://elite.finviz.com/export.ashx?v=111\&f=fa\_div\_pos,sec\_technology\&auth=YOURTOKENGESHERE
Code Examples



Google Sheets

Excel

Python

Node.js

C#
Python Code Snippet

import requests

url = "https://elite.finviz.com/export.ashx?\[allYourFilters]\&auth=YOURTOKENGOESHERE"
response = requests.get(url)
open("export.csv", "wb").write(response.content)

