import requests
from bs4 import BeautifulSoup

def scrape_indeed(query, location):
    url = f"https://fr.indeed.com/emplois?q={query}&l={location}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    jobs = []
    for job in soup.find_all('div', class_='jobsearch-ResultsList'):
        title = job.find('h2', class_='jobTitle').text.strip()
        company = job.find('span', class_='companyName').text.strip()
        location = job.find('div', class_='companyLocation').text.strip()
        jobs.append({
            'title': title,
            'company': company,
            'location': location
        })
    
    return jobs
