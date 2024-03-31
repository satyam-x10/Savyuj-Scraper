import requests
from bs4 import BeautifulSoup
import json

def extract_college_details(relative_url):
    url='https://en.wikipedia.org'+relative_url
    # print("Extracting college details from", url)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing college information
    table = soup.find('table', class_='infobox vcard')

    college_data = {}

    # Iterate through table rows (<tr>) to extract data
    if table:
      for row in table.find_all('tr'):
        # Extract key (<th>) and value (<td>) elements from each row
        th = row.find('th')
        td = row.find('td')

        # Check if both key and value elements exist
        if th and td:
            # Clean text content by removing extra whitespace and newlines
            key = th.text.strip().replace('\u00a0', ' ')
            value = td.text.strip().replace('\u00a0', ' ')

            # Save data in the college_data dictionary
            college_data[key] = value

    return college_data

def get_college_page(relative_url):
  page_url = 'https://en.wikipedia.org'+relative_url
  # print("getting page ",page_url)
  all_college_info = []
  try:
        response = requests.get(page_url)
        response.raise_for_status()  # Raise an exception for failed requests

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all th elements
        table_colleges = soup.select('table.wikitable tr')
        # Extract and print anchor tags within th elements
        count=1
        for college in table_colleges:
          college_data = {}
          college_with_link = college.find('th') or college.find('td')
          if college_with_link:
            anchor_tags = college_with_link.find_all('a')
            # print(f"Found {len(anchor_tags)} college.")

            if anchor_tags:
              college_data['Sno'] = count
              count+=1
              college_data['url'] = page_url
              college_data['Name'] = anchor_tags[0].text
              college_data['data'] = extract_college_details(anchor_tags[0]['href'])
              all_college_info.append(college_data)

  except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the webpage: {e}")


  return all_college_info

def scrape_states(url):

  universities = []
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  count=1
  # Find the table containing university information
  table = soup.find('tbody')
  # Extract information from each table row (excluding header)
  for index, row in enumerate(table.find_all('tr')):
    if index==0:  # Skip header row
      continue
    print (index,'/',len(table.find_all('tr')))
    data = {}
    # Extract university type (replace 'td' with the relevant tag)
    type_cell = row.find_all('a')  # Assuming type is in the first 'td'
    if type_cell:
      relative_url=type_cell[1]['href']
      data['Sno']= count
      data['url']=url
      count+=1
      data['State'] = type_cell[0].text.strip()
      data['University'] = get_college_page(relative_url)

    universities.append(data)

  return universities

# Scrape universities and convert to JSON
url = "https://en.wikipedia.org/wiki/List_of_universities_in_India"
universities = scrape_states(url)
json_data = json.dumps(universities, indent=4)  # Indent for readability

# Save to JSON file
with open('university.json', 'w') as outfile:
  outfile.write(json_data)

print("University information saved to universities.json")
