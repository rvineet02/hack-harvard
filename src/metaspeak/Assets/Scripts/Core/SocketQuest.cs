using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class SocketQuest : MonoBehaviour
{
    Thread mThread;
    Thread mThread2;
    public string connectionIP = "172.20.10.7"; //Laptop IP
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;
    bool running;
    public int counter = 1;
    static bool readySocket;
    static NetworkStream nwstream;

    private void Start()
    {
            readySocket = false;
            HandDebugSkeletonInfo.FirstMonitor("Oculus IP" + GetLocalIPv4());
            HandDebugSkeletonInfo.FirstMonitor(GetLocalIPv4());
            ThreadStart ts = new ThreadStart(GetInfo);
            mThread = new Thread(ts);
            mThread.Start();
            Logger.Instance.LogInfo("Monitor One");
            Logger2.Instance.LogInfo("Monitor Two");
    }

    public void Awake()
    {
        DontDestroyOnLoad(gameObject);
    }

    public void Update()
    {
        //HandDebugSkeletonInfo.TakeMessage("loop " + counter++);
        if (readySocket)
        {
            //ReceieveData();
        }
    }

    public void SayHello()
    {
        HandDebugSkeletonInfo.FirstMonitor("Hello");
    }

    public void SayShit(String shit)
    {
        HandDebugSkeletonInfo.FirstMonitor(shit);
    }

    private void GetInfo()
    {
            localAdd = IPAddress.Parse(connectionIP);
            listener = new TcpListener(IPAddress.Any, connectionPort);
            listener.Start();
            client = listener.AcceptTcpClient();
            nwstream = client.GetStream();
            readySocket = true;

            ThreadStart ts2 = new ThreadStart(ReceieveData);
            mThread2 = new Thread(ts2);
            mThread2.Start();
    }

    void ReceieveData()
    {
        while (true)
        {
            try {
                byte[] buffer = new byte[client.ReceiveBufferSize];
                int bytesRead = nwstream.Read(buffer, 0, client.ReceiveBufferSize); // //Getting data in Bytes from Python
                string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead); // Converting Bytes to String

                if (dataReceived != null)
                {
                    Logger.Instance.LogInfo("Received : " + dataReceived);
                }
            }
            catch
            {
                Logger.Instance.LogInfo("Recieve Thread Error");
            }
        }
    }

    //method to send data to HOST
    public void SendData(ArrayList alist)
    {
            if (readySocket && alist != null && nwstream != null)
            {
                string data = string.Join(",", alist.ToArray()) + "\n";
                byte[] myWriteBuffer = Encoding.UTF8.GetBytes(data);
                try
                {                           
                    nwstream.Write(myWriteBuffer, 0, myWriteBuffer.Length);
                    Logger2.Instance.LogInfo("Data Sent: " + alist[0]);
                }
                catch (Exception e)
                {
                    Logger2.Instance.LogInfo("Error: " + e.ToString());
                }
            }

    }


    public string GetLocalIPv4()
    {
        return Dns.GetHostEntry(Dns.GetHostName())
            .AddressList.First(
                f => f.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
            .ToString();
    }
}


