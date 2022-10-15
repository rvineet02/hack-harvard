using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class Game
{
	Thread mThread;
	public string connectionIP = "127.0.0.1";
	public int connectionPort = 25001;
	IPAddress localAdd;
	TcpListener listener;
	TcpClient client;
	bool running;

	public static void Main(String[] args)
	{
		Game game = new Game();
		game.StartServer();
	}

	public void StartServer()
	{
		ThreadStart ts = new ThreadStart(GetInfo);
		mThread = new Thread(ts);
		mThread.Start();
	}

	void GetInfo()
	{
		localAdd = IPAddress.Parse(connectionIP);
		listener = new TcpListener(IPAddress.Any, connectionPort);
		listener.Start();

		client = listener.AcceptTcpClient();

		running = true;
		while (running)
		{
			ReceieveData();

		}
		listener.Stop();
	}

	void ReceieveData()
	{
		NetworkStream nwstream = client.GetStream();
		byte[] buffer = new byte[client.ReceiveBufferSize];

		// Receiving data from HOST
		int bytesRead = nwstream.Read(buffer, 0, client.ReceiveBufferSize); // //Getting data in Bytes from Python
		string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead); // Converting Bytes to String

		if (dataReceived != null)
		{
			// using recieved data
			Console.WriteLine("Received : " + dataReceived);

			// sending data to HOST
			// Sends a message to a connected TcpClient.

			// create test arraylist and pass to sendData
			ArrayList test = new ArrayList();
			test.Add(1);
			test.Add(2);
			test.Add(3);
			test.Add(4);
			SendData(test, nwstream);
			// byte[] myWriteBuffer = Encoding.UTF8.GetBytes("Data Received, DO you see my message");
			// nwstream.Write(myWriteBuffer, 0, myWriteBuffer.Length); // Sending data to Python
		}
	}

	// method to send data to HOST
	void SendData(ArrayList alist, NetworkStream nwstream)
	{
		// convert arraylist to string
		string data = string.Join(",", alist.ToArray());
		// convert string to byte array
		byte[] myWriteBuffer = Encoding.UTF8.GetBytes(data);
		// send data
		nwstream.Write(myWriteBuffer, 0, myWriteBuffer.Length);
	}
}