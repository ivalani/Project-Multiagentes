// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;
    public bool has_box;

    public AgentData(string id, float x, float y, float z, bool has_box)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.has_box = has_box;
    }
}


[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData(){
        this.positions = new List<AgentData>();
    } 
}

public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8000";
    string getAgentsEndpoint = "/getRobots";
    string getObstaclesEndpoint = "/getWall";
    string getBoxesEndpoint = "/getBoxes";
    string getDropZoneEndpoint = "/getDropZone";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData, boxesData, dropZoneData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> boxesObject;
    Dictionary<string, Vector3> boxesPositions;
    Dictionary<string, Vector3> prevPositions, currPositions;
    Dictionary<string, GameObject> dropZones;
    Dictionary<string, bool> hasBoxes;
    Dictionary<string, bool> boxFlag;
    Dictionary<string, Vector3> dropZonePositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, floor;
    public GameObject box, dropZone;
    public int NAgents, width, height;
    public float boxDensity;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();
        boxesPositions = new Dictionary<string, Vector3>();
        boxesObject = new Dictionary<string, GameObject>();
        
        dropZonePositions = new Dictionary<string, Vector3>();

        hasBoxes = new Dictionary<string, bool>();
        boxFlag = new Dictionary<string, bool>();

        agents = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, (float)0.5f, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {   
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                string key = "";

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);

                if (hasBoxes[agent.Key] != boxFlag[agent.Key])
                {
                    boxFlag[agent.Key] = hasBoxes[agent.Key];
                    foreach(var boxObject in boxesPositions)
                    {
                        if (currentPosition == boxObject.Value)
                        {
                            key = boxObject.Key.ToString();
                            boxesObject[boxObject.Key.ToString()].transform.parent = agents[agent.Key].transform;
                        }
                    }
                }
            }
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentsData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NumberAgents", NAgents.ToString());
        form.AddField("BoxesDensity", boxDensity.ToString());
        form.AddField("CanvasWidth", width.ToString());
        form.AddField("CanvasHeight", height.ToString());
        

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetBoxesData());
            StartCoroutine(GetDropZoneData());

        }
    }

    IEnumerator GetAgentsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                    if(!started)
                    {
                        prevPositions[agent.id] = newAgentPosition;
                        agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                        boxFlag[agent.id] = agent.has_box;
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if(currPositions.TryGetValue(agent.id, out currentPosition))
                            prevPositions[agent.id] = currentPosition;
                        currPositions[agent.id] = newAgentPosition;
                        hasBoxes[agent.id] = agent.has_box;
                    }
            }

            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetObstacleData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetBoxesData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            boxesData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach(AgentData boxes in boxesData.positions)
            {
                var newBox = Instantiate(box, new Vector3(boxes.x, boxes.y, boxes.z), Quaternion.identity);
                boxesObject[boxes.id.ToString()] = newBox;
                boxesPositions[boxes.id.ToString()] = new Vector3(boxes.x, boxes.y, boxes.z);
            } 
        }
    }

    IEnumerator GetDropZoneData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDropZoneEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            dropZoneData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData dropZones in dropZoneData.positions)
            {
                Instantiate(dropZone, new Vector3(dropZones.x, dropZones.y, dropZones.z), Quaternion.identity);
                dropZonePositions[dropZones.id.ToString()] = new Vector3(dropZones.x, dropZones.y, dropZones.z);
            }   
        }
    }
}
