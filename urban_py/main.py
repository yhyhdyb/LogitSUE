from Network import CNetwork

if __name__ == '__main__':
    Network = CNetwork()

    # Update the file paths to your data files
    Network.ReadNode("LogitSUE/Node_SiouxFalls.txt")
    Network.ReadLink("LogitSUE/Link_SiouxFalls.txt")
    Network.ReadODpairs("LogitSUE/ODPairs_SiouxFalls.txt")
    Network.ReadPath("LogitSUE/Path_SiouxFalls.txt")

    # Run the solution algorithm
    Network.LogitSUE()
    # Display the results
