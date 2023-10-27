using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;

// 节点
public class CNode
{
    public int ID; // 节点的编号，从零开始编号
    public double PositionX; // 节点的X坐标
    public double PositionY; // 节点的Y坐标
    public int Origin_ID = -1; // 节点对应的起点编号，-1表示不是起点
    public List<int> IncomingLink = new List<int>(); // 进入节点的路段编号集合
    public List<int> OutgoingLink = new List<int>(); // 离开节点的路段编号集合	
}


// 路段
public class CLink
{
    public int ID; // 路段的编号，从零开始编号
    public CNode pInNode; // 路段的起节点
    public CNode pOutNode; // 路段的终节点
    public double FreeFlowTravelTime; // 自由流走行时间
    public double TravelTime; // 走行时间
    public double Capacity; // 路段通行能力
    public double Alpha = 0.15; // BPR函数参数，一般取0.15
    public double Power = 4.0; // BPR函数参数，一般取4.0
}


// OD对
public class CODPairs
{
    public int ID; // 起点的编号，从零开始编号
    public List<int> pODNode = new List<int>(); // OD对起点和终点的列表[O,D]
    public double ODDemand; // OD需求
    public int m_nODPath; // OD对之间的路径数量
    public List<int> pODPath = new List<int>(); // OD对之间的路径集合
    public List<double> ChoiceProb = new List<double>(); // OD对之间所有路径被选择的概率
}


// 路径path
public class CPath
{
    public int ID; // 路径的编号，从零开始编号
    public List<int> LinkInPath = new List<int>(); // 路径里的路段集合
    public double PathFlow; // 路径流量
    public double CostOfPath; // 路径费用
}

public class CNetwork
{
    // 算法参数设置
    public double Thita = 1.0; // Thita
    public double Ita = 1.5; // Ita
    public double Gama = 0.01; //Gama
    public double[] LinkFlow; // 路段流量
    public double[] DescentDirection; // 下降方向
    public double MaxUEGap = 1.0e-10; //UE的最大误差 
    public double UEGap; //UE误差
    public double CPUTime; //CPU Time
    double[] ShortestPathCost;// 最短距离
    int[] ShortestPathParent;// 最短路前继路段
    public string OutputPath = "C:\\Users\\29303\\Desktop\\urban\\LogitSUE\\output.txt"; // 输出路径

    // 四个类有关
    public List<CNode> m_Node = new List<CNode>(); //网络节点集合
    public List<CLink> m_Link = new List<CLink>(); //网络路段集合
    public List<CPath> m_Path = new List<CPath>(); //网络路径集合
    public List<CODPairs> m_ODPairs = new List<CODPairs>(); //网络的OD对集合
    public int m_nNode; //节点数
    public int m_nLink; //路段数量
    public int m_nODPairs; //起点数量
    public int m_nPath = 0; //路径数量

    // 读取节点文件
    public void ReadNode(String DataPath)
    {
        if (!File.Exists(DataPath)) // 文件是否存在
        {
            Console.WriteLine("{0} does not exist!", DataPath);
            return;
        }

        StreamReader f1 = File.OpenText(DataPath);
        string row;
        string[] Data;

        m_Node.Clear();
        m_nNode = 0;

        while ((row = f1.ReadLine()) != null)
        {
            if (row == "") continue;
            Data = row.Split('\t');
            CNode pNode = new CNode();

            pNode.ID = m_nNode;
            pNode.PositionX = Convert.ToDouble(Data[1]);
            pNode.PositionY = Convert.ToDouble(Data[2]);
            m_nNode++;
            m_Node.Add(pNode);
        }
        f1.Close();
    }

    // 读取路段文件
    public void ReadLink(string DataPath)
    {
        if (!File.Exists(DataPath)) // 文件是否存在
        {
            Console.WriteLine("{0} does not exist!", DataPath);
            return;
        }

        StreamReader f2 = File.OpenText(DataPath);
        string row;
        string[] Data;

        m_Link.Clear();
        m_nLink = 0;
        CNode pNode = new CNode();

        while ((row = f2.ReadLine()) != null)
        {
            if (row == "") continue;
            Data = row.Split('\t');
            CLink pLink = new CLink();

            pLink.ID = m_nLink;
            pLink.pInNode = (CNode)m_Node[Convert.ToInt32(Data[0]) - 1];
            pLink.pOutNode = (CNode)m_Node[Convert.ToInt32(Data[1]) - 1];
            pLink.FreeFlowTravelTime = Convert.ToDouble(Data[2]);
            pLink.Capacity = Convert.ToDouble(Data[3]);
            pLink.pInNode.OutgoingLink.Add(pLink.ID);
            pLink.pOutNode.IncomingLink.Add(pLink.ID);
            m_nLink++;
            m_Link.Add(pLink);
        }
        f2.Close();
    }

    // 读取OD对文件
    public void ReadODpairs(string DataPath)
    {
        if (!File.Exists(DataPath)) // 文件是否存在
        {
            Console.WriteLine("{0} does not exist!", DataPath);
            return;
        }

        StreamReader f3 = File.OpenText(DataPath);
        string row;
        string[] Data;

        m_ODPairs.Clear();
        m_nODPairs = 0;

        while ((row = f3.ReadLine()) != null)
        {
            if (row == "") continue;
            Data = row.Split('\t');
            CODPairs pOrigin = new CODPairs();
            pOrigin.ID = m_nODPairs;
            int ONode = Convert.ToInt32(Data[0]) - 1;
            pOrigin.pODNode.Add(ONode);
            int DNode = Convert.ToInt32(Data[1]) - 1;
            pOrigin.pODNode.Add(DNode);
            pOrigin.ODDemand = Convert.ToDouble(Data[2]);
            m_nODPairs++;
            m_ODPairs.Add(pOrigin);
        }
        f3.Close();
    }

    // 读取Path集合
    public void ReadPath(string DataPath)
    {
        if (!File.Exists(DataPath)) // 文件是否存在
        {
            Console.WriteLine("{0} does not exist!", DataPath);
            return;
        }

        StreamReader f4 = File.OpenText(DataPath);
        string row;
        string[] Data;
        CODPairs pODPairs;
        CLink pLink;

        m_Path.Clear();
        m_nPath = 0;

        pODPairs = new CODPairs();
        int numofrow = 1;
        int numofpath = 0;
        int num = 0;
        while ((row = f4.ReadLine()) != null)
        {
            if (row == "") continue;
            Data = row.Split('\t');

            if (numofrow == 1)
            {
                // 第一行
                int ODPairsID = Convert.ToInt32(Data[0]) - 1;
                int ONode = Convert.ToInt32(Data[1]) - 1;
                int DNode = Convert.ToInt32(Data[2]) - 1;
                numofpath = Convert.ToInt32(Data[3]);
                pODPairs = m_ODPairs[ODPairsID];
                pODPairs.m_nODPath = numofpath;
                numofrow++;
                continue;
            }

            if (num < numofpath)
            {
                num++;
                CPath pPath = new CPath();
                pPath.ID = m_nPath; // ID
                pODPairs.pODPath.Add(pPath.ID); // 加入OD对->path的索引
                int linkinN = Convert.ToInt32(Data[0]) - 1;
                for (int node = 1; node < Data.Length; node++)  // 在path中添加LinkInPath
                {
                    int linkoutN = Convert.ToInt32(Data[node]) - 1;
                    for (int link = 0; link < m_nLink; link++)
                    {
                        pLink = m_Link[link];
                        if ((linkinN == pLink.pInNode.ID) & (linkoutN == pLink.pOutNode.ID))
                        {
                            pPath.LinkInPath.Add(link);
                        }
                    }
                    linkinN = linkoutN;
                }
                m_Path.Add(pPath);
                m_nPath++;
                continue;
            }
            else
            {
                num = 0;
                int ODPairsID = Convert.ToInt32(Data[0]) - 1;
                int ONode = Convert.ToInt32(Data[1]) - 1;
                int DNode = Convert.ToInt32(Data[2]) - 1;
                numofpath = Convert.ToInt32(Data[3]);
                pODPairs = m_ODPairs[ODPairsID];
                pODPairs.m_nODPath = numofpath;
            }
        }
        f4.Close();
    }
    // 计算路径选择概率
    public List<double> RouteChoiceProb(int odpairs)
    {
        CODPairs pODPairs;
        CPath pPath;

        double Sum = 0;
        List<double> ChoiceProb = new List<double>();
        pODPairs = m_ODPairs[odpairs];
        foreach (int path in pODPairs.pODPath)
        {
            pPath = m_Path[path];
            double LogitPara = Math.Exp(-Thita * pPath.CostOfPath);
            Sum += LogitPara;
            ChoiceProb.Add(LogitPara);
        }

        for (int index = 0; index < ChoiceProb.Count; index++)
        {
            ChoiceProb[index] /= Sum;
        }
        return ChoiceProb;
    }

    // 间隙函数
    /* 说明：
       （1）输入：初始路段流量LinkFlow（索引对应CLink中的ID）
       （2）输出：间隙函数值
    */
    public double GetUEGap(double[] LinkFlow)   //获取UE的误差
    {
        CODPairs pODPairs;
        CLink pLink;

        // 计算被减项分母 + 更新路段走行时间（出行费用：TravelTime）
        double num1 = 0;
        for (int link = 0; link < m_nLink; link++)
        {
            pLink = m_Link[link];
            // 更新TravelTime
            pLink.TravelTime = BPR(pLink.FreeFlowTravelTime, LinkFlow[link], pLink.Capacity);
            // 单一求和项的计算
            num1 += (pLink.TravelTime * LinkFlow[link]);
        }

        // 计算被减项分子
        double num2 = 0;
        for (int odpairs = 0; odpairs < m_nODPairs; odpairs++) // 遍历OD对的循环
        {
            pODPairs = m_ODPairs[odpairs];
            int OriginNode = pODPairs.pODNode[0];
            int DestinationNode = pODPairs.pODNode[1];
            double Demand = pODPairs.ODDemand;
            double ODCost = GetShortestCost(OriginNode, DestinationNode);
            num2 += (Demand * ODCost);
        }

        // 计算间隙函数
        UEGap = 1 - num2 / num1;

        return UEGap;
    }

    // 求解BPR函数
    /* 说明：
       （1）输入：路段的自由流出行费用、路段流量和通行能力
       （2）输出：路段阻抗
    */
    public double BPR(double FreeFlowTravelTime, double Flow, double Capacity)
    {
        double BPRValue;
        BPRValue = FreeFlowTravelTime * (1 + 0.15 * Math.Pow(Flow / Capacity, 4));
        return BPRValue;
    }

    // 计算向量的模
    public double Norm(double[] Vector)
    {
        double Sum = 0;
        foreach (double index in Vector)
        {
            Sum += Math.Pow(index, 2);
        }
        return (Math.Sqrt(Sum));
    }

    // 计算最短路距离
    /* 说明：
       （1）输入：起点、终点的NodeId
       （2）输出：最短路径上的 *最短距离*
    */
    public double GetShortestCost(int Start, int End)
    {
        CNode pNode;
        CLink pLink;
        // 初始化
        int startposition = 0, endposition = 1;
        ShortestPathCost = new double[m_nNode]; //当前最短路
        ShortestPathParent = new int[m_nNode]; //前驱节点
        int[] checkList = new int[m_nNode];//队列，循环使用
        bool[] binCheckList = new bool[m_nNode]; //是否在队列中
        bool[] bscanStatus = new bool[m_nNode];

        for (int node = 0; node < m_nNode; node++)
        {
            ShortestPathParent[node] = -1;
            ShortestPathCost[node] = double.MaxValue;
            binCheckList[node] = false;
        }
        ShortestPathCost[Start] = 0;
        checkList[0] = Start;

        //开始while循环
        while (startposition != endposition)
        {
            if (startposition >= m_nNode) startposition = 0;
            int i = checkList[startposition];
            startposition++;
            pNode = m_Node[i];
            for (int index = 0; index < pNode.OutgoingLink.Count; index++)
            {
                pLink = m_Link[pNode.OutgoingLink[index]];
                int j = pLink.pOutNode.ID;
                double value = pLink.TravelTime;
                if (ShortestPathCost[j] > ShortestPathCost[i] + value)
                {
                    ShortestPathCost[j] = ShortestPathCost[i] + value;
                    ShortestPathParent[j] = i;
                    // 添加到队列尾部
                    if (endposition >= m_nNode) endposition = 0;
                    checkList[endposition] = j;
                    endposition++;
                    bscanStatus[j] = true;
                }
            }
        }
        // 返回最短路距离
        return ShortestPathCost[End];
    }

    // 用自适应平均法求解SUE交通分配问题
    public void LogitSUE()
    {
        CLink pLink;
        CPath pPath;
        CODPairs pODPairs;

        // 初始化
        int K = 1; // 迭代次数
        double Beta = 1;
        long begtime = DateTime.Now.Ticks;

        // （1）基于自由流走行时间更新路径出行费用
        for (int path = 0; path < m_nPath; path++)
        {
            pPath = m_Path[path];
            pPath.CostOfPath = 0;
            foreach (int link in pPath.LinkInPath)
            {
                pLink = m_Link[link];
                pPath.CostOfPath += pLink.FreeFlowTravelTime;
            }
        }
        // （2）计算路径选择概率
        for (int odpairs = 0; odpairs < m_nODPairs; odpairs++)
        {
            pODPairs = m_ODPairs[odpairs];
            pODPairs.ChoiceProb = RouteChoiceProb(odpairs);
        }
        // （3）计算路径流量
        for (int odpairs = 0; odpairs < m_nODPairs; odpairs++)
        {
            pODPairs = m_ODPairs[odpairs];
            double Demand = pODPairs.ODDemand;
            for (int path = 0; path < pODPairs.m_nODPath; path++)
            {
                pPath = m_Path[pODPairs.pODPath[path]];
                double Prob = pODPairs.ChoiceProb[path];
                pPath.PathFlow = Demand * Prob;
            }
        }
        // （4）计算初始路段流量
        LinkFlow = new double[m_nLink];
        for (int path = 0; path < m_nPath; path++)
        {
            pPath = m_Path[path];
            foreach (int link in pPath.LinkInPath)
            {
                LinkFlow[link] += pPath.PathFlow;
            }
        }
        // （5）初始化下降方向DescentDirection
        DescentDirection = new double[m_nLink];
        for (int link = 0; link < m_nLink; link++)
        {
            DescentDirection[link] = LinkFlow[link];
        }

        // 开始while循环
        double NormD = Norm(DescentDirection);
        using (TextWriter tw = File.CreateText(OutputPath))
        {
            while (NormD > MaxUEGap)
            {
                // 根据路段流量更新路径阻抗
                for (int link = 0; link < m_nLink; link++)
                {
                    pLink = m_Link[link];
                    pLink.TravelTime = BPR(pLink.FreeFlowTravelTime, LinkFlow[link], pLink.Capacity);
                }
                for (int path = 0; path < m_nPath; path++)
                {
                    pPath = m_Path[path];
                    pPath.CostOfPath = 0;
                    foreach (int link in pPath.LinkInPath)
                    {
                        pLink = m_Link[link];
                        pPath.CostOfPath += pLink.TravelTime;
                    }
                }
                // 计算路径选择概率
                for (int odpairs = 0; odpairs < m_nODPairs; odpairs++)
                {
                    pODPairs = m_ODPairs[odpairs];
                    pODPairs.ChoiceProb = RouteChoiceProb(odpairs);
                }
                // 计算路径流量
                for (int odpairs = 0; odpairs < m_nODPairs; odpairs++)
                {
                    pODPairs = m_ODPairs[odpairs];
                    double Demand = pODPairs.ODDemand;
                    for (int path = 0; path < pODPairs.m_nODPath; path++)
                    {
                        pPath = m_Path[pODPairs.pODPath[path]];
                        double Prob = pODPairs.ChoiceProb[path];
                        pPath.PathFlow = Demand * Prob;
                    }
                }
                // 利用公式计算可行下降方向
                double[] NewLinkFlow = new double[m_nLink];
                for (int path = 0; path < m_nPath; path++)
                {
                    pPath = m_Path[path];
                    foreach (int link in pPath.LinkInPath)
                    {
                        NewLinkFlow[link] += pPath.PathFlow;
                    }
                }
                for (int link = 0; link < m_nLink; link++)
                {
                    DescentDirection[link] = LinkFlow[link] - NewLinkFlow[link];
                }


                // 开始if判断
                double NewNormD = Norm(DescentDirection);
                if (NewNormD >= NormD)
                {
                    Beta += Ita;
                }
                else
                {
                    Beta += Gama;
                }
                NormD = NewNormD;
                // 确定步长
                double Lamuda = 1 / Beta;
                // 更新路段流量
                for (int link = 0; link < m_nLink; link++)
                {
                    LinkFlow[link] -= Lamuda * DescentDirection[link];
                }
                K++;


                Console.WriteLine("K:" + K);
                Console.WriteLine("NormD:" + NormD);
                Console.WriteLine();

                UEGap = GetUEGap(LinkFlow);
                long nowtime = DateTime.Now.Ticks;
                CPUTime = (nowtime - begtime) / 10000000.0;
                tw.WriteLine(K + "," + NormD + "," + CPUTime);
            }
        }
        // 输出结果
        // 平衡流量
        double Z = 0; // 目标函数
        Console.WriteLine("算法结果");
        Console.WriteLine("Link：" + m_nLink);
        Console.WriteLine("ID" + "\t\t" + "Flow" + "\t\t" + "Cost");
        for (int link = 0; link < m_nLink; link++)
        {
            pLink = m_Link[link];
            double flow = Math.Round((LinkFlow[link]), 0);
            double cost = Math.Round((pLink.TravelTime), 2);
            Console.WriteLine(link + "\t\t" + flow + "\t\t" + cost);
            Z += pLink.FreeFlowTravelTime * (LinkFlow[link] + 0.03 * Math.Pow(LinkFlow[link], 5) / Math.Pow(pLink.Capacity, 4));
        }
        Console.WriteLine();
        double SumCost = 0; // 目标函数
        for (int path = 0; path < m_nPath; path++)
        {
            pPath = m_Path[path];
            double flow = Math.Round((pPath.PathFlow), 0);
            double cost = Math.Round((pPath.CostOfPath), 2);
            int O = m_Link[pPath.LinkInPath[0]].pInNode.ID + 1;
            int D = m_Link[pPath.LinkInPath[pPath.LinkInPath.Count - 1]].pOutNode.ID + 1;
            SumCost += pPath.PathFlow * pPath.CostOfPath;
        }
        Console.WriteLine();
        Console.WriteLine("迭代次数：" + K);
        Console.WriteLine("目标函数：" + Z);
        Console.WriteLine("总阻抗  ：" + SumCost);
        double endtime = DateTime.Now.Ticks;
        CPUTime = (endtime - begtime) / 10000000.0;
        double time = Math.Round((CPUTime), 2);
        Console.WriteLine("CPUTime ：" + time + "秒");
    }
}