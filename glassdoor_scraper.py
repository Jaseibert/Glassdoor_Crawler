from lxml import html, etree
import requests
import re
import os
import sys
import unicodecsv as csv
import argparse
import json
import datetime
import selenium


def parse(keyword, place):
	headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'accept-encoding': 'gzip, deflate, sdch, br',
				'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
				'referer': 'https://www.glassdoor.com/',
				'upgrade-insecure-requests': '1',
				'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
				'Cache-Control': 'no-cache',
				'Connection': 'keep-alive' }

	location_headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.01',
						'accept-encoding': 'gzip, deflate, sdch, br',
						'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
						'referer': 'https://www.glassdoor.com/',
						'upgrade-insecure-requests': '1',
						'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
						'Cache-Control': 'no-cache',
						'Connection': 'keep-alive'}

	data = {"term": place,
			"maxLocationsToReturn": 10}

	location_url = "https://www.glassdoor.co.in/findPopularLocationAjax.htm?"
	try:
		# Getting location id for search location
		print("Fetching location details")
		location_response = requests.post(location_url, headers=location_headers, data=data).json()
		place_id = location_response[0]['locationId']
		job_litsting_url = 'https://www.glassdoor.com/Job/jobs.htm'

		# Form data to get job results
		data = {
			'clickSource': 'searchBtn',
			'sc.keyword': keyword,
			'locT': 'C',
			'locId': place_id,
			'jobType': ''}

		job_listings = []

		if place_id:
			response = requests.post(job_litsting_url, headers=headers, data=data)
			# extracting data from
			# https://www.glassdoor.com/Job/jobs.htm?suggestCount=100&suggestChosen=true&clickSource=searchBtn&typedKeyword=andr&sc.keyword=android+developer&locT=C&locId=1146821&jobType=
			parser = html.fromstring(response.text)
			# Making absolute url
			base_url = "https://www.glassdoor.com"
			parser.make_links_absolute(base_url)

			XPATH_ALL_JOB = '//li[@class="jl"]'
			XPATH_NAME = './/a/text()'
			XPATH_JOB_URL = './/a/@href'
			XPATH_LOC = './/span[@class="subtle loc"]/text()'
			XPATH_COMPANY = ".//div[@class='jobInfoItem jobEmpolyerName']/text()"
			XPATH_SALARY = './/span[@class="salaryText"]/text()'
			XPATH_NEXT = '//li[@class="next"]//a/@href'

			listings = parser.xpath(XPATH_ALL_JOB)

			for job in listings:
				raw_job_name = job.xpath(XPATH_NAME)
				raw_job_url = job.xpath(XPATH_JOB_URL)
				raw_lob_loc = job.xpath(XPATH_LOC)
				raw_company = job.xpath(XPATH_COMPANY)
				raw_salary = job.xpath(XPATH_SALARY)

				# Cleaning data
				job_name = ''.join(raw_job_name).strip('–') if raw_job_name else None
				job_location = ''.join(raw_lob_loc) if raw_lob_loc else None
				raw_state = re.findall(",\s?(.*)\s?", job_location)
				state = ''.join(raw_state).strip()
				raw_city = job_location.replace(state, '')
				city = raw_city.replace(',', '').strip()
				company = ''.join(raw_company).replace('–','')
				salary = ''.join(raw_salary).strip()
				job_url = raw_job_url[0] if raw_job_url else None


				jobs = {
					"Name": job_name,
					"Company": company,
					"State": state,
					"City": city,
					"Salary": salary,
					"Location": job_location,
					"Url": job_url,
				}

				job_listings.append(jobs)
			link = job.xpath(XPATH_NEXT)
			return job_listings
		else:
			print("location id not available")
	except:
		print("Failed to load locations")


name = input(str("Hey There, what is your name?:  "))
JobID = ['Data Scientist', 'Data Analyst','Software Engineer']
Cities = ['Austin', 'Nashville','Atlanta','Denver','Portland']

def itterate(JobID, Cities):
	for job in JobID:
		for city in Cities:
			print("Fetching job details for {}s in {}.".format(job, city))
			scraped_data = parse(job, city)
			print("Writing data to output file '{}_Jobs/{}s-{}-job-results.csv'".format(name, job, city))
			with open('{}_Jobs/{}s-{}-job-results.csv'.format(name, job, city), 'wb') as csvfile:
				fieldnames = ['Name', 'Company', 'State', 'City', 'Salary', 'Location', 'Url']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)
				writer.writeheader()
				if scraped_data:
					for data in scraped_data:
						writer.writerow(data)
				else:
					print("Hey {}! Your search for {}s, in {} does not match any jobs".format(name,job,city))

itterate(JobID,Cities)
