import math
import time
import os

class Node:
    def __init__(self):
        self.ID = 0
        self.PositionX = 0.0
        self.PositionY = 0.0
        self.Origin_ID = -1
        self.IncomingLink = []
        self.OutgoingLink = []

class Link:
    def __init__(self):
        self.ID = 0
        self.pInNode = None
        self.pOutNode = None
        self.FreeFlowTravelTime = 0.0
        self.TravelTime = 0.0
        self.Capacity = 0.0
        self.Alpha = 0.15
        self.Power = 4.0

class ODPairs:
    def __init__(self):
        self.ID = 0
        self.pODNode = []
        self.ODDemand = 0.0
        self.m_nODPath = 0
        self.pODPath = []
        self.ChoiceProb = []

class Path:
    def __init__(self):
        self.ID = 0
        self.LinkInPath = []
        self.PathFlow = 0.0
        self.CostOfPath = 0.0

class CNetwork:
    def __init__(self):
        self.Thita = 1.0
        self.Ita = 1.5
        self.Gama = 0.01
        self.LinkFlow = []
        self.DescentDirection = []
        self.MaxUEGap = 1.0e-10
        self.UEGap = 0.0
        self.CPUTime = 0.0
        self.ShortestPathCost = []
        self.ShortestPathParent = []
        self.OutputPath = "output.txt"
        self.m_Node = []
        self.m_Link = []
        self.m_Path = []
        self.m_ODPairs = []
        self.m_nNode = 0
        self.m_nLink = 0
        self.m_nODPairs = 0
        self.m_nPath = 0

    def ReadNode(self, DataPath):
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        self.m_Node = []
        self.m_nNode = 0
        with open(DataPath, 'r') as f1:
            for row in f1:
                if row == "":
                    continue
                Data = row.split('\t')
                pNode = Node()
                pNode.ID = self.m_nNode
                pNode.PositionX = float(Data[1])
                pNode.PositionY = float(Data[2])
                self.m_nNode += 1
                self.m_Node.append(pNode)

    def ReadLink(self, DataPath):
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        self.m_Link = []
        self.m_nLink = 0
        with open(DataPath, 'r') as f2:

            for row in f2:
                if row == "":
                    continue
                Data = row.split('\t')
                pLink = Link()
                pLink.ID = self.m_nLink
                pLink.pInNode = self.m_Node[int(Data[0]) - 1]
                pLink.pOutNode = self.m_Node[int(Data[1]) - 1]
                pLink.FreeFlowTravelTime = float(Data[2])
                pLink.Capacity = float(Data[3])
                pLink.pInNode.OutgoingLink.append(pLink.ID)
                pLink.pOutNode.IncomingLink.append(pLink.ID)
                self.m_nLink += 1
                self.m_Link.append(pLink)

    def ReadODpairs(self, DataPath):
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        m_ODPairs = []
        m_nODPairs = 0
        with open(DataPath, 'r') as f3:
            for row in f3:
                if row == "":
                    continue
                Data = row.split('\t')
                pOrigin = ODPairs()
                pOrigin.ID = m_nODPairs
                ONode = int(Data[0]) - 1
                pOrigin.pODNode.append(ONode)
                DNode = int(Data[1]) - 1
                pOrigin.pODNode.append(DNode)
                pOrigin.ODDemand = float(Data[2])
                self.m_nODPairs += 1
                self.m_ODPairs.append(pOrigin)


    def ReadPath(self, DataPath):
        if not os.path.exists(DataPath):
            print(f"{DataPath} does not exist!")
            return
        self.m_Path = []
        self.m_nPath = 0
        with open(DataPath, 'r') as f4:
            pODPairs = ODPairs()
            numofrow = 1
            numofpath = 0
            num = 0
            for row in f4:
                if row == "":
                    continue
                Data = row.split('\t')

                if numofrow == 1:
                    ODPairsID = int(Data[0]) - 1
                    numofpath = int(Data[3])
                    pODPairs = self.m_ODPairs[ODPairsID]
                    pODPairs.m_nODPath = numofpath
                    numofrow += 1
                    continue

                if num < numofpath:
                    num += 1
                    pPath = Path()
                    pPath.ID = self.m_nPath
                    pODPairs.pODPath.append(pPath.ID)
                    linkinN = int(Data[0]) - 1
                    for node in range(1, len(Data)):
                        linkoutN = int(Data[node]) - 1
                        for link in range(self.m_nLink):
                            pLink = self.m_Link[link]
                            if (linkinN == pLink.pInNode.ID) and (linkoutN == pLink.pOutNode.ID):
                                pPath.LinkInPath.append(link)
                        linkinN = linkoutN
                    self.m_Path.append(pPath)
                    self.m_nPath += 1
                    continue
                else:
                    num = 0
                    ODPairsID = int(Data[0]) - 1
                    numofpath = int(Data[3])
                    pODPairs = self.m_ODPairs[ODPairsID]
                    pODPairs.m_nODPath = numofpath

    def RouteChoiceProb(self, odpairs):
        pODPairs = self.m_ODPairs[odpairs]
        ChoiceProb = []
        Sum = 0
        for path in pODPairs.pODPath:
            pPath = self.m_Path[path]
            LogitPara = math.exp(-self.Thita * pPath.CostOfPath)
            Sum += LogitPara
            ChoiceProb.append(LogitPara)

        for index in range(len(ChoiceProb)):
            ChoiceProb[index] /= Sum
        return ChoiceProb

    def GetUEGap(self, LinkFlow):
        num1 = 0
        for link in range(self.m_nLink):
            pLink = self.m_Link[link]
            pLink.TravelTime = self.BPR(pLink.FreeFlowTravelTime, LinkFlow[link], pLink.Capacity)
            num1 += (pLink.TravelTime * LinkFlow[link])

        num2 = 0
        for odpairs in range(self.m_nODPairs):
            pODPairs = self.m_ODPairs[odpairs]
            OriginNode = pODPairs.pODNode[0]
            DestinationNode = pODPairs.pODNode[1]
            Demand = pODPairs.ODDemand
            ODCost = self.GetShortestCost(OriginNode, DestinationNode)
            num2 += (Demand * ODCost)

        UEGap = 1 - num2 / num1
        return UEGap

    def BPR(self, FreeFlowTravelTime, Flow, Capacity):
        BPRValue = FreeFlowTravelTime * (1 + 0.15 * (Flow / Capacity) ** 4)
        return BPRValue

    def Norm(self, Vector):
        Sum = 0
        for value in Vector:
            Sum += value ** 2
        return math.sqrt(Sum)

    def GetShortestCost(self, Start, End):
        startposition = 0
        endposition = 1
        ShortestPathCost = [float('inf')] * self.m_nNode
        ShortestPathParent = [-1] * self.m_nNode
        checkList = [0] * self.m_nNode
        binCheckList = [False] * self.m_nNode
        bscanStatus = [False] * self.m_nNode

        ShortestPathCost[Start] = 0
        checkList[0] = Start

        while startposition != endposition:
            if startposition >= self.m_nNode:
                startposition = 0
            i = checkList[startposition]
            startposition += 1
            pNode = self.m_Node[i]
            for index in range(len(pNode.OutgoingLink)):
                pLink = self.m_Link[pNode.OutgoingLink[index]]
                j = pLink.pOutNode.ID
                value = pLink.TravelTime
                if ShortestPathCost[j] > ShortestPathCost[i] + value:
                    ShortestPathCost[j] = ShortestPathCost[i] + value
                    ShortestPathParent[j] = i
                    if endposition >= self.m_nNode:
                        endposition = 0
                    checkList[endposition] = j
                    endposition += 1
                    bscanStatus[j] = True
        return ShortestPathCost[End]

    def LogitSUE(self):
        K = 1
        Beta = 1
        begtime = time.time()

        for path in self.m_Path:
            path.CostOfPath = 0
            for link in path.LinkInPath:
                pLink = self.m_Link[link]
                path.CostOfPath += pLink.FreeFlowTravelTime

        for odpairs in range(self.m_nODPairs):
            pODPairs = self.m_ODPairs[odpairs]
            pODPairs.ChoiceProb = self.RouteChoiceProb(odpairs)

        for odpairs in range(self.m_nODPairs):
            pODPairs = self.m_ODPairs[odpairs]
            Demand = pODPairs.ODDemand
            for path in range(pODPairs.m_nODPath):
                pPath = self.m_Path[pODPairs.pODPath[path]]
                Prob = pODPairs.ChoiceProb[path]
                pPath.PathFlow = Demand * Prob

        LinkFlow = [0] * self.m_nLink

        for path in range(self.m_nPath):
            pPath = self.m_Path[path]
            for link in pPath.LinkInPath:
                LinkFlow[link] += pPath.PathFlow

        DescentDirection = LinkFlow[:]

        NormD = self.Norm(DescentDirection)

        with open(self.OutputPath, 'w') as tw:
            while NormD > self.MaxUEGap:
                for link in range(self.m_nLink):
                    pLink = self.m_Link[link]
                    pLink.TravelTime = self.BPR(pLink.FreeFlowTravelTime, LinkFlow[link], pLink.Capacity)

                for path in range(self.m_nPath):
                    pPath = self.m_Path[path]
                    pPath.CostOfPath = 0
                    for link in pPath.LinkInPath:
                        pLink = self.m_Link[link]
                        pPath.CostOfPath += pLink.TravelTime

                for odpairs in range(self.m_nODPairs):
                    pODPairs = self.m_ODPairs[odpairs]
                    pODPairs.ChoiceProb = self.RouteChoiceProb(odpairs)

                for odpairs in range(self.m_nODPairs):
                    pODPairs = self.m_ODPairs[odpairs]
                    Demand = pODPairs.ODDemand
                    for path in range(pODPairs.m_nODPath):
                        pPath = self.m_Path[pODPairs.pODPath[path]]
                        Prob = pODPairs.ChoiceProb[path]
                        pPath.PathFlow = Demand * Prob

                NewLinkFlow = [0] * self.m_nLink

                for path in self.m_Path:
                    for link in path.LinkInPath:
                        NewLinkFlow[link] += path.PathFlow

                DescentDirection = [LinkFlow[i] - NewLinkFlow[i] for i in range(self.m_nLink)]
                NewNormD = self.Norm(DescentDirection)

                if NewNormD >= NormD:
                    Beta += self.Ita
                else:
                    Beta += self.Gama

                NormD = NewNormD
                Lamuda = 1 / Beta

                for link in range(self.m_nLink):
                    LinkFlow[link] -= Lamuda * DescentDirection[link]

                K += 1

                print("K:", K)
                print("NormD:", NormD)
                print()

                self.UEGap = self.GetUEGap(LinkFlow)
                nowtime = time.time()
                CPUTime = nowtime - begtime
                tw.write(f"{K},{NormD},{CPUTime}\n")

        Z = 0
        print("Algorithm Result")
        print("Link:", self.m_nLink)
        print("ID\t\tFlow\t\tCost")
        for link in range(self.m_nLink):
            pLink = self.m_Link[link]
            flow = round(LinkFlow[link], 0)
            cost = round(pLink.TravelTime, 2)
            print(f"{link}\t\t{flow}\t\t{cost}")
            Z += pLink.FreeFlowTravelTime * (LinkFlow[link] + 0.03 * (LinkFlow[link] ** 5) / (pLink.Capacity ** 4))

        print()
        SumCost = 0
        for path in self.m_Path:
            flow = round(path.PathFlow, 0)
            cost = round(path.CostOfPath, 2)
            O = self.m_Link[path.LinkInPath[0]].pInNode.ID + 1
            D = self.m_Link[path.LinkInPath[-1]].pOutNode.ID + 1
            SumCost += path.PathFlow * path.CostOfPath

        print()
        print("Number of Iterations:", K)
        print("Objective Function:", Z)
        print("Total Impedance:", SumCost)
        endtime = time.time()
        CPUTime = endtime - begtime
        print(f"CPUTime: {CPUTime} seconds")

