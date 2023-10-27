using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

    namespace WT_LogitSUE
    {
        class Program
        {
            static void Main(string[] args)
            {
                CNetwork Network = new CNetwork();

                // 读取文件
                Network.ReadNode("C:\\Users\\29303\\Desktop\\urban\\LogitSUE\\Node_SiouxFalls.txt");
                Network.ReadLink("C:\\Users\\29303\\Desktop\\urban\\LogitSUE\\Link_SiouxFalls.txt");
                Network.ReadODpairs("C:\\Users\\29303\\Desktop\\urban\\LogitSUE\\ODPairs_SiouxFalls.txt");
                Network.ReadPath("C:\\Users\\29303\\Desktop\\urban\\LogitSUE\\Path_SiouxFalls.txt");

                // 运行求解算法
                Network.LogitSUE();
                // 显示结果
                Console.ReadKey();
            }
        }
    }

