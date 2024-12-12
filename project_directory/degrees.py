import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Source Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Target Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Load source as sourceNode
    sourceNode = Node(state = source, parent = None, action = None)

    # Get search strategy
    strategy = input("Choose search strategy (DFS/BFS): ").strip().upper()
    if strategy not in {"DFS", "BFS"}:
        sys.exit("Invalid strategy. Please choose 'DFS' or 'BFS'.")

    # Select strategy either DFS or BFS based on user input
    if strategy == "DFS":
        frontier = StackFrontier()
    elif strategy == "BFS":
        frontier = QueueFrontier()
    
    # Add the source node to the frontier
    frontier.add(sourceNode)

    # Set of explored states
    explored = set()

    # Incrementer to assess how many nodes DFS vs BFS will look at
    numExploredNodes = 0

    # Loop the frontier while it is not empty to check if the target has been found and to access neighbors
    while not frontier.empty():
        # Remove a node from the frontier for testing
        currNode = frontier.remove()
        numExploredNodes += 1

        if currNode.state == target:
            # Reconstruct the path from the source to the target
            path = []
            while currNode.parent is not None:
                path.append((currNode.action, currNode.state))
                currNode = currNode.parent
            path.reverse()

            print(f"Number of nodes explored {numExploredNodes}")
            return path
        
        # If not target node then add it to the explored 
        explored.add(currNode.state)

        # Use neighbors_for_person function to add neighbors to the frontier
        neighbors = neighbors_for_person(currNode.state)
        for movie, person in neighbors:
            if person not in explored and not frontier.contains_state(person):
                child = Node(state = person, parent = currNode, action = movie)
                frontier.add(child)

    # If not path is found still print the number of nodes and return none
    print(f"Number of nodes explored: {numExploredNodes}")
    return None



def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
