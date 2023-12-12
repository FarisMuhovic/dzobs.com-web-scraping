# Project Overview

Jobs are scraped from dzobs.com. The jobs gathered are not older than 30 days.

### Web Scraping

Web scraping of the dzobs.com webpage is accomplished using the Python library Scrapy. The scraped data is then filtered and stored in a MongoDB collection.

### Scrapy Commands

1. **Create a Scrapy project:**

   ```bash
   scrapy startproject project_name
   ```

2. **Generate a new spider within a project:**

   ```bash
   scrapy genspider spider_name example.com
   ```

3. **Run a spider:**

   ```bash
   scrapy crawl spider_name
   ```

4. **Run a spider and save the output to a JSON file:**

   ```bash
   scrapy crawl spider_name -o output.json
   ```

5. **View available spiders in a project:**
   ```bash
   scrapy list
   ```
6. **_Current spider table_**

   | Name        | Web domain | Command                    |
   | ----------- | ---------- | -------------------------- |
   | dzobsSpider | dzobs.com  | `scrapy crawl dzobsSpider` |

### Setting up Environment Variables

To maintain a secure development environment, enviroment variables are used for Scrapy.

Create a `.env` file in the root of your Scrapy project(in web_scrapping folder) and populate it with the required variables. Use the provided `.env.example` as a template.

Example `.env.example`:

```env
# .env.example
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=abc
COLLECTION_NAME=abc

```

**Author:** Faris Muhovic **Educational Use Only:** This project is intended for educational purposes. Ensure compliance with the terms of service of the websites being scraped.
