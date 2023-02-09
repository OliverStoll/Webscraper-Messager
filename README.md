# General Purpose Webscraper & Messager
This webscraper is designed to scrape & possible message generic content from websites that offer lists of such data.
Applications can range from job offers, apartment listings or even news articles.

# How it works
- The scraper takes multiple websites as input
- It then scrapes the content from the websites using one content_element selector per website
- Then, it filters the content based on a set of filters
- Finally, it sends a website-form message through each contents' detail pages
- All website layouts are specified in the `SCRAPER` as well as the `MESSAGER` parts of the config.yaml file.

# How to use locally

### Build
`pyinstaller --onefile main.py --distpath .  --name "Webscraper" --icon=res/icon.ico --log-level=WARN --specpath build/Webscraper`

### Schedule
To use the executable with Windows Task Scheduler, create a scheduled Task and set "Start in" as the project directory 