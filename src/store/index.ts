import { defineStore } from "pinia";
import axios from "axios";

axios.defaults.baseURL = "http://localhost:8081";

export interface node {
  ID: number;
  PositionX: number;
  PositionY: number;
  Origin_ID: number;
  IncomingLink: number[];
  OutgoingLink: number[];
  isSelected: false;
}

export interface Link {
  ID: number;
  pInNode: number;
  pOutNode: number;
  FreeFlowTravelTime: number;
  Capacity: number;
  isSelected: false;
}

export interface ODPairs {
  ID: number;
  pODNode: number[];
  ODDemand: number;
  pODPath: number[];
  ChioceProb: number[];
}

export interface Path {
  ID: number;
  LinkInPath: number[];
  PathFlow: number;
  CostOfPath: number;
}

export const useNetworkStore = defineStore({
  id: "network",
  state: () => ({
    nodes: [] as node[],
    links: [] as unknown[],
    odPairs: [] as unknown[],
    paths: [] as unknown[],
  }),
  actions: {
    async fetchNodes() {
      const response = await axios.get<node[]>("/nodes");
      this.nodes = response.data;
      console.log(this.nodes);
    },
    async fetchLinks() {
      const response = await axios.get<Link[]>("/links");
      this.links = response.data;
      //console.log(this.links);
    },
    async fetchODPairs() {
      const response = await axios.get<ODPairs[]>("/odpairs");
      this.odPairs = response.data;
      //console.log(this.odPairs);
    },
    async fetchPaths() {
      const response = await axios.get<Path[]>("/paths");
      this.paths = response.data;
      //console.log(this.paths);
    },
  },
});
