from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

nodes = []
connections = []

disallowed_sites = []
robots_url = "robots.txt"

depth = 0
top_n_nodes = 5

def branch(site, current_depth = 0):

    #check robots.txt
    
    try:
        robots_response = requests.get(site + robots_url, timeout=5)

    except requests.exceptions.Timeout:
        print("Request timed out from site ", site)
        disallowed_sites.append(site)
        return
    
    except requests.exceptions.ConnectionError as e:  #SSL errors
        print(f"Cannot connect to site ", site, " :", e)
        disallowed_sites.append(site)
        return

    robots_response = robots_response.text.split("\n\n")  #get robots.txt text, and split into user-agent sections

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

        link_url = link.get('href').replace("?", "/").split("/")

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
        if next_site not in nodes and next_site not in disallowed_sites and current_depth < depth:

            #continue crawling to next site
            branch(next_site, current_depth + 1) 


def build_matrix():

    global nodes
    global connections
    
    #add missing nodes to the node list
    
    #M must be a node x node matrix, and right now there might be some nodes in the connections list that aren't in the nodes list 
    #(for example, nodes that we haven't visited because max depth was reached). That's why we add the missing nodes.

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

    while depth < 3 or depth > 6:
        depth = int(input("Please enter the depth of the algorithm (between 3 and 6): "))

    #start crawling

    root_url = "https://google.com/"
    # root_url = "https://24ur.com/"
    # root_url = "https://feri.um.si/"

    branch(root_url)


    #build M and find ranks

    M = build_matrix()

    N = np.full((len(nodes), len(nodes)), 1 / len(nodes))

    beta = 0.85     #probability of teleporting to a random connection

    A = beta * M + (1 - beta) * N

    r0 = np.full(len(nodes), 1 / len(nodes))    #starting rank

    ranks = []

    epsilon = 0.001  #convergence threshhold

    iteration_counter = 0

    while True:

        ranks = A.dot(r0)

        iteration_counter += 1

        print("Iteration ", iteration_counter, ": \n", ranks, "\n")

        if (abs(ranks[0] - r0[0]) < epsilon):
            break

        r0 = ranks

    print("Convergence achieved after ", iteration_counter, " iterations.\n")


    #sort by rank

    while (len(connections) != len(nodes)):
        connections.append([])  #add an empty list for each node that doesn't lead to another site


    #sort rank list, node list and connection list by rank value
    ranks, nodes, connections = (list(t) for t in zip(*sorted(zip(ranks, nodes, connections), reverse=True)))


    #print the nodes and their ranks
    print("Final ranks: \n")
    for i in range(len(nodes)):
        print(("{} -> {:.6f}".format(nodes[i], ranks[i])))


    #draw the graph

    #format nodes for better graph representation
    for i in range(len(nodes)):
        nodes[i] = nodes[i].removeprefix("https://").removesuffix("/")

    for i in range(len(connections)):
        for j in range(len(connections[i])):
            connections[i][j] = connections[i][j].removeprefix("https://").removesuffix("/")

    G = nx.DiGraph()
    labels = {}
    node_sizes = []

    #separated next two for loops due to possibility of some url being the predecessor of another, and ther later appearing in the top top_n_nodes

    #add top_n_nodes (sorted by rank), their labels and sizes to graph
    for i in range(top_n_nodes): 

        G.add_node(nodes[i])
        labels[nodes[i]] = "{}\n{:.3f}".format(nodes[i], ranks[i])
        node_sizes.append(ranks[i] * 100000) 

    #add nodes that lead to top_n_nodes, their labels and sizes
    for i in range(top_n_nodes):

        for j in range(len(connections)):
            for k in range(len(connections[j])):

                if (nodes[i] == connections[j][k]):

                    if (nodes[j] not in G.nodes):

                        G.add_node(nodes[j])
                        labels[nodes[j]] = "{}\n{:.3f}".format(nodes[j], ranks[j])
                        node_sizes.append(ranks[j] * 100000)

                    G.add_edge(nodes[j], nodes[i])

    pos = nx.spring_layout(G, seed = 50, k=5)

    plt.figure(figsize=(20, 10))
    nx.draw(G, pos, ax = None, with_labels = True, labels=labels, font_size = 10, node_size = node_sizes, node_color = 'lightgreen')

    root_url = root_url.removeprefix("https://").removesuffix(".com/")
    # root_url = root_url.removeprefix("https://").removesuffix(".um.si/")

    plt.savefig("{}_{}.png".format(root_url, depth))


