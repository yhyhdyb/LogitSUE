from Network import CNetwork
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/nodes')
def get_nodes():
    nodes = []
    for node in Network.m_Node:
        nodes.append({
            'ID': node.ID,
            'PositionX': node.PositionX,
            'PositionY': node.PositionY,
            'Origin_ID': node.Origin_ID,
            'IncomingLink': node.IncomingLink,
            'OutgoingLink': node.OutgoingLink
        })
    return jsonify(nodes)

@app.route('/links')
def get_links():
    links = []
    for link in Network.m_Link:
        links.append({
            'ID': link.ID,
            'pInNode': link.pInNode.ID,
            'pOutNode': link.pOutNode.ID,
            'FreeFlowTravelTime': link.FreeFlowTravelTime,
            'Capacity': link.Capacity,
        })
    return jsonify({'links': links})
#pinnode poutnode是Node的ID

@app.route('/odpairs')
def getOdPairs():
    odPairs = []
    for odPair in Network.m_ODPairs:
        odPairs.append({
            'ID': odPair.ID,
            'pODNode': odPair.pODNode,
            'ODDemand': odPair.ODDemand,
            'pODPath': odPair.pODPath,
            'ChoiceProb': odPair.ChoiceProb,
        })
    return jsonify({'odPairs': odPairs})

@app.route('/paths')
def getPaths():
    paths = []
    for path in Network.m_Path:
        paths.append({
            'ID': path.ID,
            'LinkInPath': path.LinkInPath,
            'PathFlow': path.PathFlow,
            'CostOfPath': path.CostOfPath,
        })
    return jsonify({'odPairs': paths})

if __name__ == '__main__':
    Network = CNetwork()

    # Update the file paths to your data files
    Network.ReadNode("py/LogitSUE/Node_SiouxFalls.txt")
    Network.ReadLink("py/LogitSUE/Link_SiouxFalls.txt")
    Network.ReadODpairs("py/LogitSUE/ODPairs_SiouxFalls.txt")
    Network.ReadPath("py/LogitSUE/Path_SiouxFalls.txt")

    # Run the solution algorithm
    Network.LogitSUE()
    app.run(debug=True,port=8081)
    # Display the results
