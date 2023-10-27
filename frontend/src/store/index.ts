import { defineStore } from "pinia";
import axios from "axios";

axios.defaults.baseURL = "http://localhost:8081";
interface Node {
  ID: number;
  PositionX: number;
  PositionY: number;
  Origin_ID: number;
  IncomingLink: number[];
  OutgoingLink: number[];
}

interface Link {
  ID: number;
  pInNode: number;
  pOutNode: number;
  FreeFlowTravelTime: number;
  Capacity: number;
}

interface ODPairs {
  ID: number;
  pODNode: number[];
  ODDemand: number;
  pODPath: number[];
  ChioceProb: number[];
}

interface Path {
  ID: number;
  LinkInPath: number[];
  PathFlow: number;
  CostOfPath: number;
}

export const useNetworkStore = defineStore({
  id: "network",
  state: () => ({
    nodes: [] as Node[],
    links: [] as Link[],
    odPairs: [] as ODPairs[],
    paths: [] as Path[],
  }),
  actions: {
    async fetchNodes() {
      const response = await axios.get<Node[]>("/nodes");
      this.nodes = response.data;
    },
    async fetchLinks() {
      const response = await axios.get<Link[]>("/links");
      this.links = response.data;
    },
    async fetchODPairs() {
      const response = await axios.get<ODPairs[]>("/odpairs");
      this.odPairs = response.data;
    },
    async fetchPaths() {
      const response = await axios.get<Path[]>("/paths");
      this.paths = response.data;
    },
  },
});
