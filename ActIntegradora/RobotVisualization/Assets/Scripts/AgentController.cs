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
public class WallData 
{
    public string id;
    public float x, y, z;

    public WallData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }

}
[Serializable]
public class RobotData
{
    public string id;
    public float x, y, z;
    public bool withPackage;

    public RobotData(string id, bool withPackage, float x, float y, float z)
    {
        this.id = id;
        this.withPackage = withPackage;
        this.x = x;
        this.y = y;
        this.z = y;
    }
}
[Serializable]
public class DropZoneData
{
    public string id;
    public int numberBoxes;
    public float x, y, z;

    public DropZoneData(string id, int numberBoxes, float x, float y, float z)
    {
        this.id = id;
        this.numberBoxes = numberBoxes;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class BoxData
{
    public string id;
    public bool picked;
    public float x, y, z;

    public BoxData(string id, bool picked, float x, float y, float z)
    {
        this.id = id;
        this.picked = picked;
        this.x = x;
        this.y = y;
        this.z =z;
    }
}

[Serializable]
public class WallsData
{
    public List<WallData> data;

    public WallsData() => this.data = new List<WallData>();

}

[Serializable]
public class RobotsData
{
    public List<RobotData> data;

    public RobotsData() => this.data = new List<RobotData>();
}

[Serializable]

public class DropZonesData
{
    public List<DropZoneData> data;

    public DropZonesData() => this.data = new List<DropZoneData>();
}

[Serializable]
public class BoxesData
{
    public List<BoxData> data;

    public BoxesData() => this.data = new List<BoxData>();

}

public class AgentController: MonoBehaviour
{
    /*Endpoints routes*/
    string serverUrl = "http://localhost:8000";
    string sendConfigEndpoint = "/init";
    string getRobots = "/getRobots";
    string getWall = "/getWall";
    string getBoxes = "/getBoxes";
    string getDropZone = "/getDropZone";
    string update = "/update";

    WallsData wallsData;
    RobotsData robotsData;
    DropZonesData dropZonesData;
    BoxesData boxesData;

    Dictionary<string, GameObject> robots, dropzones, boxes;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false;
    bool robotsStarted = false;
    bool dropZonesStarted = false;
    bool boxesStarted = false;
    public GameObject robotPrefab, wallPrefab, floor, boxPrefab;
    public GameObject box, dropZone;
    public int NAgents, width, height;
    public float BoxesDensity;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        robotsData = new RobotsData();
        dropZonesData = new DropZonesData();
        boxesData = new BoxesData();
        wallsData = new WallsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        robots = new Dictionary<string, GameObject>();
        dropzones = new Dictionary<string, GameObject>();
        boxes = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        StartCoroutine(setConfiguration());
    }

    /// <summary>
    /// Update is called every frame, if the MonoBehaviour is enabled.
    /// </summary>
    void Update()
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(updateSimulation());
        }

        if(updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPositon = agent.Value;
                Vector3 previousPositon = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPositon, currentPositon, dt);
                Vector3 direction = currentPositon - interpolated;

                robots[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero)
                    robots[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                
            }
        }
    }


    IEnumerator setConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NumberAgents", NAgents.ToString());
        form.AddField("BoxesDensity", BoxesDensity.ToString());
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
            StartCoroutine(getAgentsData());
            StartCoroutine(getBoxData());
            StartCoroutine(getDropZoneData());
            StartCoroutine(getWallData());
            Debug.Log("Created instances!");
            
        }

    }

    IEnumerator getAgentsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRobots);

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            robotsData = JsonUtility.FromJson<RobotsData>(www.downloadHandler.text);

            // Update the positions of the agents
            foreach(RobotData agent in robotsData.data)
            {
                Vector3 newRobotPosition = new Vector3(agent.x, agent.y, agent.z);

                if(!robotsStarted)
                {
                    prevPositions[agent.id] = newRobotPosition;
                    robots[agent.id] = Instantiate(robotPrefab, newRobotPosition, Quaternion.identity);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if(currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newRobotPosition;

                    if(agent.withPackage)
                    {
                        robots[agent.id].transform.GetChild(0).gameObject.SetActive(true);
                    }
                    else
                    {
                        robots[agent.id].transform.GetChild(0).gameObject.SetActive(false);
                    }
                }
            }

            updated = true;
            if(!robotsStarted) robotsStarted = true;
        }
    }

    IEnumerator getBoxData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxes);

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            boxesData = JsonUtility.FromJson<BoxesData>(www.downloadHandler.text);
            
            foreach(BoxData box in boxesData.data)
            {
                if(!boxesStarted)
                {
                    boxes[box.id] = Instantiate(boxPrefab, new Vector3(box.x, box.y, box.z), Quaternion.identity);
                }
                else
                {
                    if(box.picked)
                    {
                        boxes[box.id].SetActive(false);
                    }else
                    {
                        boxes[box.id].SetActive(true);
                    }
                }
            }

            updated = true;
            if(boxesStarted) boxesStarted = true;
        }
    }

    IEnumerator getWallData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getWall);

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            wallsData = JsonUtility.FromJson<WallsData>(www.downloadHandler.text);
            
            foreach(WallData wall in wallsData.data)
            {
                Instantiate(wallPrefab, new Vector3(wall.x, wall.y, wall.z), Quaternion.identity);
            }

        }
    }

    IEnumerator getDropZoneData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDropZone);

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            dropZonesData = JsonUtility.FromJson<DropZonesData>(www.downloadHandler.text);

            foreach(DropZoneData dropZone in dropZonesData.data)
            {
                if(dropZone.numberBoxes == 0)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(3).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(false);
                } else if (dropZone.numberBoxes == 1)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(3).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(false);
                } else if (dropZone.numberBoxes == 2)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(3).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(false);
                } else if (dropZone.numberBoxes == 3)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(3).gameObject.SetActive(false);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(false);
                }else if (dropZone.numberBoxes == 4)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(3).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(false);
                }else if (dropZone.numberBoxes == 5)
                {
                    dropzones[dropZone.id].transform.GetChild(0).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(1).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(2).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(4).gameObject.SetActive(true);
                    dropzones[dropZone.id].transform.GetChild(5).gameObject.SetActive(true);
                }
            }
        }

        updated = true;
        if(!dropZonesStarted) dropZonesStarted = true;
    }

    IEnumerator updateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + update);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(getAgentsData());
            StartCoroutine(getDropZoneData());
            StartCoroutine(getBoxData());
        } 
    }
}
