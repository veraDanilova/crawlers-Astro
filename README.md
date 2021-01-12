# crawlers-Astro
Scrapy-based spiders to perform regular crawling of three databases of observations and check for the mentions of target objects. Updates the corresponding recording files.

== REQUIREMENTS ==
Python==3.5
Scrapy==1.5
pip
datefinder (pip install datefinder)

==RUN==
bash: enter the folder "astro/astro/spiders" where the script astrospider.py is contained.
Run the following command: "python astrospider.py" to run the spider once a day at the same time, at this hour

==OUTPUT==
folder astro/crawling_results

