import scrapy
from ..pipelines import MongoDBConnector
from scrapy.linkextractors import LinkExtractor
import os
from dotenv import load_dotenv
load_dotenv()

class Dzobsspider(scrapy.Spider):
    name = "dzobsSpider"
    allowed_domains = ["dzobs.com"]
    start_urls = ["https://www.dzobs.com/poslovi/1"]

    db_settings = {
        # second parameter is default value.
        'MONGO_URI': os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', 'jobs'),
        'COLLECTION_NAME': os.getenv('COLLECTION_NAME', 'dzobs'),
    }

    def __init__(self, *args, **kwargs):
        super(Dzobsspider, self).__init__(*args, **kwargs)
        self.mongo_connector = MongoDBConnector(
            connection_string=self.db_settings.get('MONGO_URI'),
            database_name=self.db_settings.get('DATABASE_NAME'),
            collection_name=self.db_settings.get('COLLECTION_NAME')
        )
    def start_requests(self):
        self.mongo_connector.drop_collection()
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse)
        
    def spider_closed(self, spider, reason):
        self.mongo_connector.close_connection()
        

    def parse(self, response):
        for job in response.css('.job-shadow'):
            job_title = job.css('h3.font-medium::text').get()
            company_name = job.css('div.text-gray-dark.font-light::text').get()
            location = job.xpath('/html/body/div/div/div[3]/a[5]/div/div[2]/div[1]/div[2]/text()').get()
            is_remote = job.xpath('/html/body/div/div/div[3]/a[1]/div/div[1]/div[2]/div/div/span/text() | /html/body/div/div/div[3]/a[1]/div/div[1]/div[2]/div/div/span//text()').get()
            experience = job.xpath('/html/body/div/div/div[3]/a[1]/div/div[2]/div[2]/div[2]//text()').get()
            experience = experience.split(', ')
            detailed_job_url = job.xpath('..//@href').get()
            deadline = job.xpath('/html/body/div/div/div[3]/a[1]/div/div[2]/div[3]/div[2]//text()').getall()
            deadline = deadline[1]

            if is_remote:
                is_remote = True
            else:
                is_remote = False

            if detailed_job_url:
                yield scrapy.Request(
                        url=response.urljoin(detailed_job_url),
                        callback=self.parse_detailed_job,
                        meta={
                            'job_title': job_title,
                            'company_name': company_name, 
                            'location': location, 
                            'is_remote': is_remote, 
                            'experience': experience, 
                            'detailed_job_url': detailed_job_url, 
                            'deadline': deadline}
                        )
            else:
                self.save_data_to_db(job_title, company_name, location, is_remote, experience, deadline)

        # Get other pages
        yield from self.extract_other_pages(response)


    def extract_other_pages(self,response):
        le = LinkExtractor()
        links = le.extract_links(response)
        pagination_links = [link for link in links if '/poslovi/' in link.url]
        for link in pagination_links:
            yield scrapy.Request(url=link.url, callback=self.parse)

    def log_job_info(self, job_title, company_name, location, is_remote, experience, detailed_job_url, deadline, technologies ,worktime, about_company, job_description, qualifications, website_link ):
        self.logger.info(f"Job Title: {job_title}")
        self.logger.info(f"Company Name: {company_name}")
        self.logger.info(f"Location: {location}")
        self.logger.info(f"Is remote: {is_remote}")
        self.logger.info(f"Experience: {experience}")
        self.logger.info(f"Detailed job url: {detailed_job_url}")
        self.logger.info(f"Deadline for job application(in days): {deadline}")
        self.logger.info(f"Technologies used: {technologies}")
        self.logger.info(f"Worktime: {worktime}")
        self.logger.info(f"About company: {about_company}\n")
        self.logger.info(f"Job description: {job_description}\n")
        self.logger.info(f"Qualifications: {qualifications}\n")
        self.logger.info(f"Website link: {website_link}")
        self.logger.info('------------------------------------------------')\
        
    def parse_detailed_job(self, response):
        # meta fields
        job_title = response.meta.get('job_title')
        company_name = response.meta.get('company_name')
        location = response.meta.get('location')
        is_remote = response.meta.get('is_remote')
        experience = response.meta.get('experience')
        detailed_job_url = response.meta.get('detailed_job_url')
        deadline = response.meta.get('deadline')
       # scraped fields
        technologies = response.css('.inline-block.mx-2.hover\\:text-blue.underline::text').getall()
        worktime = response.xpath('/html/body/div/div/div[2]/div[1]/div/div/div[2]/div[2]//text()').get()
        about_company = response.css('div.pt-16 > section:first-child span::text').getall()
        job_description = response.css('div.pt-16 > section:nth-child(2) span::text').getall()
        qualifications = response.css('div.pt-16 > section:nth-child(3) span::text').getall()
        company_info_link = response.css('.mb-3 > a:nth-child(1)::attr(href)').get()

        if company_info_link:
            yield scrapy.Request(
                url=response.urljoin(company_info_link),
                callback=self.parse_company_website_link,
                meta={
                    'job_title': job_title, 
                    'company_name': company_name,
                    'location': location, 
                    'is_remote': is_remote,
                    'experience': experience,
                    'detailed_job_url': detailed_job_url, 
                    'deadline': deadline, 
                    'technologies': technologies, 
                    'worktime': worktime, 
                    'about_company': about_company, 
                    'job_description': job_description, 
                    'qualifications': qualifications,
                },
                dont_filter=True # dont filter duplicate values, because multiple jobs can be from same company website
            )
        else:
            self.save_data_to_db(job_title, company_name, location, is_remote, experience, deadline, detailed_job_url , technologies, worktime, about_company,job_description,qualifications)
           
    def parse_company_website_link(self, response):
        # meta fields
        job_title = response.meta.get('job_title')
        company_name = response.meta.get('company_name')
        location = response.meta.get('location')
        is_remote = response.meta.get('is_remote')
        experience = response.meta.get('experience')
        detailed_job_url = response.meta.get('detailed_job_url')
        deadline = response.meta.get('deadline')
        technologies = response.meta.get('technologies')
        worktime = response.meta.get('technologies')
        about_company = response.meta.get('about_company')
        job_description = response.meta.get('job_description')
        qualifications = response.meta.get('qualifications')
        # scraped fields
        website_link = response.css('a:contains("Website")::attr(href)').get()

        self.log_job_info(job_title, company_name, location, is_remote, experience, detailed_job_url, deadline, technologies, worktime, about_company,job_description,qualifications, website_link )
        
        self.save_data_to_db(job_title, company_name, location, is_remote, experience, deadline, detailed_job_url , technologies, worktime, about_company,job_description,qualifications, website_link)

    def save_data_to_db(self, job_title, company_name, location, is_remote, experience, deadline, detailed_job_url = "", technologies = [] , worktime = "" , about_company = [], job_description = [], qualifications = [], website_link = "" ):
        data = {
            'job_title': job_title, 
            'company_name': company_name, 
            'location': location,
            'is_remote': is_remote, 
            'experience':experience, 
            'detailed_job_url': detailed_job_url,
            'deadline': deadline,
            'technologies': technologies,
            'worktime': worktime,
            'about_company': about_company,
            'job_description': job_description,
            'qualifications': qualifications,
            'website_link': website_link
            }
        self.mongo_connector.insert_data(data)