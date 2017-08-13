#####################################################################
#Code by- Sampanna Pathak
#Idea from Hardvard University CS109 2015
#Parsing through the indeed.com database for a given job title and
#find out how many jobs mention certain skills to priortize the learning
#of skills
#Plot them graphically using bar chart
#Send the numbers over text message over twilio api
#Python 3
#####################################################################


#Import all the required libraries
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import re
import time
import urllib3
from bs4 import BeautifulSoup
import _pickle as pickle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import matplotlib.pyplot as plt
from twilio.rest import Client

#List of Job descriptions to search for
job_descriptions = ['big data developer','data science']

#Dictionary with the skill sets we are looking for
skill_set = {'mapreduce':0,'spark':0,'yarn':0,'flume':0,'sqoop':0,'hive':0,'pig':0,'sql':0,'hbase':0,'kafka':0,'cassandra':0,'storm':0,'mongodb':0}

job_links=[]
job_postings=[]
job_id=[]
each_digit_in_string=[]
number_of_errors = 0
number_of_jobs = 0

#Create a function to scarape through the webpage
def scrape(job_des,skills):
	for each_job_des in job_des:  #iterate through each job description
		split_each_job_des = []
		modify_each_job_des = each_job_des.replace(" ","+")
		
		# indeed.com url for a particular job description
		url = 'http://www.indeed.com/jobs?q=' + modify_each_job_des + '&l='
		
		#parse the content on the webpage using urllib3 and beautifulsoup libraries
		http = urllib3.PoolManager()
		url_response = http.request('GET',url)
		souped_web = BeautifulSoup(url_response.data,"lxml")

		#look for searchCount id to get the total number of jobs
		total_jobs_search_count = souped_web.find(id="searchCount")
		total_jobs_search_string = total_jobs_search_count.contents[0].split(" ")[-1]

		#convert the total number of jobs string to number
		each_digit_in_string = [int(d) for d in total_jobs_search_string if d.isdigit()]
		total_jobs_search_int = np.sum(digit*(10**exponent) for digit,exponent in zip(each_digit_in_string[::-1],range(len(each_digit_in_string))))
		print ("Total number of jobs found is",total_jobs_search_int)

		#parse through each page. In this case 10 pages
		iterate = 20
		for i in range(iterate):
			#print (i)
			page_url = 'http://www.indeed.com/jobs?q=' + modify_each_job_des + '&start=' + str(i*10)
			#print (page_url)
			page_url_read = http.request('GET',page_url)
			souped_page_url = BeautifulSoup(page_url_read.data,"lxml")

			#find the body by searching for resultCol id
			body = souped_page_url.find(id='resultsCol')
	
			#find all lines with div id and class as rowreslt 
			job_posting = body.findAll("div")
			job_postings = [jp for jp in job_posting if not jp.get('class') is None and ''.join(jp.get('class'))=="rowresult"]
			job_id = [jp.get('data-jk') for jp in job_postings]
			#print(len(job_id))

			#link for each search result
			for each_id in job_id:
				#print(j)
				job_links.append('https://www.indeed.com/rc/clk?jk=' + each_id)

			time.sleep(1)

		print ("Parsing through {} jobs " .format(len(job_links)))

		#pickle the job links so no need to scare again	
		with open('scraped_links.pkl','wb') as f:
			pickle.dump(job_links,f)

	global number_of_jobs
	global number_of_errors
	for link in job_links:
		
		number_of_jobs +=1
		
		try:
			
			job_url = http.request('GET',link)
			job_url_data = job_url.data
			job_url_data_lower = job_url_data.lower()
		except:
			#print ("Error")
			number_of_errors +=1
			continue

		for key in skill_set.keys():
			if key.encode() in job_url_data_lower:
				skill_set[key] +=1

	print ("There were {} errors when {} jobs were parsed".format(number_of_errors,number_of_jobs))
	return skill_set





skill_set = scrape(job_descriptions,skill_set)
print (skill_set)
#OrderedDict(sorted(skill_set.items(),key=lambda x: x[0]))

plt.figure()
x=[]
y=[]
for key,value in skill_set.items():
	x.append(key)
	y.append(value)

x1 = np.arange(len(y))
print (y)
plt.bar(x1,y,align='center')
plt.xticks(x1,x)
#plt.show()

display_message = "There were " + str(number_of_errors) + " errors in " + str(number_of_jobs) + " jobs parsed...........\n" + str(skill_set.items())
print(display_message)


account_sid = "xxxxxxx"
auth_token = "xxxxxxxx"

client = Client(account_sid, auth_token)

client.messages.create(
    to="+1xxxxxxxxxx",
    from_="+1xxxxxxxxxx",
    body= display_message)

plt.show()

