from bs4 import BeautifulSoup
import requests
import re
import numpy as np

visited_urls = []
seen_urls = []
# visited_urls_count = []
robots_url = "robots.txt"
max_depth = 1

def branch(site, current_depth):

    #check robots.txt first
    robots_response = requests.get(site + robots_url).text
    robots_response = robots_response.split("\n\n")

    for i in range (len(robots_response)):

        user_agent_conf = robots_response[i].split("\n")

        if (user_agent_conf[0] != "User-agent: *"):
            continue
        else:
            if ("Disallow: /" in user_agent_conf):
                print("Access to site ", site, " is disallowed, continue...")
                return

    available_urls = []

    response = requests.get(site).text

    soup = BeautifulSoup(response, 'html.parser')

    for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):

        link_url = link.get('href').split("/")
        parsed_url = "/".join(link_url[:3]) + "/"

        parsed_url = parsed_url.replace("www.", "")

        available_urls.append(parsed_url)

    visited_urls.append(site)           #nodes (- leaves)
    seen_urls.append(available_urls)    #connections

    # visited_urls_count.append(len(available_urls))
    # print("Current depth: ", current_depth)

    for i in range(len(available_urls)):

        # if current_depth < max_depth:

        if available_urls[i] not in visited_urls and current_depth < max_depth:
            branch(available_urls[i], current_depth + 1)

    # print("Hello from site: ", site)
    # print(available_urls)
    # print("\n")

def build_matrix():

    visited_urls = ['https://google.com/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://google.si/', 'https://accounts.google.com/']

    seen_urls = [['https://google.com/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://news.google.com/', 'https://mail.google.com/', 'https://drive.google.com/', 'https://google.si/', 'https://accounts.google.com/', 'https://google.com/'], 
                 ['https://accounts.google.com/', 'https://accounts.google.com/', 'https://policies.google.com/', 'https://consent.google.si/', 'https://policies.google.com/', 'https://policies.google.com/'],
                 ['https://policies.google.com/', 'https://myaccount.google.com/', 'https://play.google.com/', 'https://support.google.com/', 'https://support.google.com/', 'https://support.google.com/', 'https://play.google.com/', 'https://policies.google.com/', 'https://support.google.com/', 'https://store.google.com/'], 
                 ['https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 'https://developers.google.com/', 'https://youtube.com/', 'https://youtube.com/'],
                 ['https://google.si/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://news.google.com/', 'https://mail.google.com/', 'https://drive.google.com/', 'https://google.si/', 'https://accounts.google.com/', 'https://google.si/'], 
                 ['https://support.google.com/', 'https://support.google.com/', 'https://accounts.google.com/', 'https://accounts.google.com/']]

    # visited_urls = ['y', 'a', 'm']

    # seen_urls = [['y', 'a'], ['y', 'm'], ['m']]

    unique_sites = visited_urls.copy()

    # for i in range(len(seen_urls)):
    #     for j in range(len(seen_urls[i])):
    #         if seen_urls[i][j] not in unique_sites:
    #             unique_sites.append(seen_urls[i][j])

    #now we have the dimensions of matrix M
    dimension = len(unique_sites)
    matrix = np.zeros((dimension, dimension))

    for i in range(dimension): #for unique sites

        for j in range(len(seen_urls)):

            # print("Length of ", j, ": ", len(seen_urls[j]))
            for k in range(len(seen_urls[j])):

                if (unique_sites[i] == seen_urls[j][k]):

                    #find the number of connections from that node

                    matrix[i][j] += (1 / len(seen_urls[j]))

    return matrix


# branch("https://google.com/", 0)
# branch("https://24ur.com/", 0) 

# print("Visited: ")
# print(visited_urls)

# print("Seen: ")
# print(seen_urls)

M = build_matrix()

print(M)

# branch("https://facebook.com/", 0)

# print("\n\nFinal count: ")
# for i in range (len(visited_urls)):
#     print(visited_urls[i], " count: ", visited_urls_count[i])

