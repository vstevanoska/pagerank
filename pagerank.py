from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import sys
import networkx as nx
import matplotlib.pyplot as plt


nodes = []
connections = []

disallowed_sites = []
robots_url = "robots.txt"

max_depth = 5
top_n_nodes = 5

np.set_printoptions(threshold=sys.maxsize)

def branch(site, current_depth = 0):

    #check robots.txt

    robots_response = (requests.get(site + robots_url).text).split("\n\n")  #get robots.txt text, and split into user-agent sections

    for user_agent_section in robots_response:

        if (user_agent_section.startswith("User-agent: *")):                #get User-agent: * section

            user_agent_conf = user_agent_section.split("\n")                #and split further into lines

            if ("Disallow: /" in user_agent_conf):                              #if access to the whole site is disallowed,
                print("Access to site ", site, " is disallowed, continue...")
                disallowed_sites.append(site)                                   #add the site to the disallowed list,
                return                                                          #and don't crawl through it
            
            break 


    #get links from site

    available_urls = []

    response = requests.get(site).text              #get response from site

    soup = BeautifulSoup(response, 'html.parser')   #parse response

    for link in soup.find_all('a', attrs={'href': re.compile("^https://")}):    #find all a href tags

        link_url = link.get('href').split("/")
        formatted_url = ("/".join(link_url[:3]) + "/").replace("www.", "")      #format url (remove www., keep everything up until (and including) top-level domain)

        available_urls.append(formatted_url)


    #add links to nodes and connections

    global nodes
    global connections

    nodes.append(site)
    connections.append(available_urls)


    #continue crawling to available sites

    for next_site in available_urls:

        #if the next site hasn't been visited before, and it's not on the list of disallowed sites, and if the current depth is within the limit
        if next_site not in nodes and next_site not in disallowed_sites and current_depth < max_depth:

            #continue crawling to next site
            branch(next_site, current_depth + 1) 


def build_matrix():

    global nodes
    global connections

    nodes = ['https://google.com/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://google.si/', 
                    'https://accounts.google.com/']

    connections = [['https://google.com/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://news.google.com/', 
                  'https://mail.google.com/', 'https://drive.google.com/', 'https://google.si/', 'https://accounts.google.com/', 'https://google.com/'], 
                 
                 ['https://accounts.google.com/', 'https://accounts.google.com/', 'https://policies.google.com/', 'https://consent.google.si/', 
                  'https://policies.google.com/', 'https://policies.google.com/'],

                 ['https://policies.google.com/', 'https://myaccount.google.com/', 'https://play.google.com/', 'https://support.google.com/', 
                  'https://support.google.com/', 'https://support.google.com/', 'https://play.google.com/', 'https://policies.google.com/', 
                  'https://support.google.com/', 'https://store.google.com/'], 

                 ['https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 'https://youtube.com/', 
                  'https://developers.google.com/', 'https://youtube.com/', 'https://youtube.com/'],

                 ['https://google.si/', 'https://maps.google.si/', 'https://play.google.com/', 'https://youtube.com/', 'https://news.google.com/', 
                  'https://mail.google.com/', 'https://drive.google.com/', 'https://google.si/', 'https://accounts.google.com/', 'https://google.si/'],

                 ['https://support.google.com/', 'https://support.google.com/', 'https://accounts.google.com/', 'https://accounts.google.com/']]


    #add missing nodes to the node list

    for connection_list in connections:
        for url in connection_list:
            if url not in nodes:
                nodes.append(url)


    #initialize matrix M

    M = np.zeros((len(nodes), len(nodes)))


    #fill values of M

    for i in range(len(nodes)):

        for j in range(len(connections)):

            for k in range(len(connections[j])):

                #if the node at position j leads to the node at position i (that is at position [j][k] in connections)
                if (nodes[i] == connections[j][k]):

                    M[i][j] += (1 / len(connections[j]))

    return M


if __name__ == "__main__":

    #start crawling

    root_url = "https://google.com/"
    # root_url = "https://24ur.com/"

    # branch(root_url)


    #build M and find ranks

    M = build_matrix()

    N = np.full((len(nodes), len(nodes)), 1 / len(nodes))

    beta = 0.85     #probability of teleporting to a random connection

    A = beta * M + (1 - beta) * N

    r0 = np.full(len(nodes), 1 / len(nodes))    #starting rank

    ranks = []

    epsilon = 0.01  #value of convergence

    iteration_counter = 0

    while True:

        ranks = A.dot(r0)

        if (abs(ranks[0] - r0[0]) < epsilon):
            break

        r0 = ranks

        iteration_counter += 1

    print("Convergence achieved after ", iteration_counter, " iterations")


    #sort by rank

    while (len(connections) != len(nodes)):
        connections.append([])  #add an empty list for each node that doesn't lead to another site


    #sort rank list, node list and connection list by rank value
    ranks, nodes, connections = (list(t) for t in zip(*sorted(zip(ranks, nodes, connections), reverse=True)))


    #print the nodes and their ranks
    print(("{} -> {:.3f}".format(nodes[i], ranks[i])) for i in range(len(nodes)))


    #draw the graph

    #drop https:// from unique_sites and seen_urls
    for i in range(len(nodes)):
        nodes[i] = nodes[i].removeprefix("https://").removesuffix("/")

    for i in range(len(connections)):
        for j in range(len(connections[i])):
            connections[i][j] = connections[i][j].removeprefix("https://").removesuffix("/")

    G = nx.DiGraph()
    labels = {}
    node_sizes = []

    for i in range(top_n_nodes):  #separate for loop due to the possibility of some url being the predecessor of another, and then later being in the top 5

        print(nodes[i])
        G.add_node(nodes[i])
        labels[nodes[i]] = "{}\n{:.3f}".format(nodes[i], ranks[i])
        node_sizes.append(ranks[i] * 100000) 

    for i in range(len(nodes[:5])):

        for j in range(len(connections)):
            for k in range(len(connections[j])):

                if (nodes[i] == connections[j][k]):

                    if (nodes[j] not in G.nodes):

                        G.add_node(nodes[j])
                        labels[nodes[j]] = "{}\n{:.3f}".format(nodes[j], ranks[j])
                        node_sizes.append(ranks[j] * 100000)

                    G.add_edge(nodes[j], nodes[i])

    pos = nx.spring_layout(G, seed = 50, k=5)

    nx.draw(G, pos, ax = None, with_labels = True, labels=labels, font_size = 10, node_size = node_sizes, node_color = 'lightgreen')
    plt.savefig("fig_{}.png".format(max_depth)) #change maxdepth


