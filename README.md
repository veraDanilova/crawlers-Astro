# crawlers-Astro
Scrapy-based spiders to perform regular crawling of three databases of observations and check for the mentions of target objects. Updates the corresponding recording files.\n\n

== REQUIREMENTS ==\n
Python==3.5\n
Scrapy==1.5\n
pip\n
datefinder (pip install datefinder)\n
\n
==RUN==\n
bash: enter the folder "astro/astro/spiders" where the script astrospider.py is contained.
Run the following command: "python astrospider.py" to run the spider once a day at the same time, at this hour
\n\n
==OUTPUT==\n
folder astro/crawling_results

