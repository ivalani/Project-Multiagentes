using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

/*Classes for agent data*/
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
    
    public bool has_box; 

    public RobotData(string id, float x, float y, float z, bool has_box)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z; 
        this.has_box = has_box;
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
        this.z = z;
    }

}

/*Agents data lists*/
[Serializable]
public class WallsData
{
    public List<WallData> positions;

    public WallsData() => this.positions = new List<WallData>();
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
public class BoxesData
{
    public List<BoxData> data;
    public BoxesData() => this.data = new List<BoxData>();
}
public class AgentsController : MonoBehaviour
{
    string server = "http://localhost:8000";
    string getRobots = "/getRobots";
    string getBoxes = "/getBoxes";
    string getWall = "/getWall";
    string getDropZone = "/getDropZone";
    string sendConfig = "/init";
    string update = "/update";
    

    WallsData wallsData;
    RobotsData robotsData;
    DropZonesData dropZoneData;
    BoxesData boxesData;
    Dictionary<string, GameObject> robots, dropzones, boxes;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, robotsStarted = false, dropZoneStarted = false, BoxesStarted = false;

    public GameObject robotPrefab, wallPrefab, boxPrefab, dropZonePrefab, floor;
    public int NAgents, width, height;
    public float boxDensity;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    // Start is called before the first frame update
    void Start()
    {
        robotsData = new RobotsData();
        dropZoneData = new DropZonesData();
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

        StartCoroutine(sendConfiguration());
    }

    // Update is called once per frame
    void Update()
    {
        if(timer < 0)
        {
            timer -= timeToUpdate;
            updated = false;
            StartCoroutine(updateSimulation());

        }

        if(updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                robots[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) robots[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }

    IEnumerator sendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NumberAgents", NAgents.ToString());
        form.AddField("BoxesDensity", boxDensity.ToString());
        form.AddField("CanvasWidth", width.ToString());
        form.AddField("CanvasHeight", height.ToString());
        

        UnityWebRequest www = UnityWebRequest.Post(server + sendConfig, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);

        }else
        {
            Debug.Log("Configuration uploaded!");
            Debug.Log("Getting agents data");
            StartCoroutine(getWallData());
            StartCoroutine(getRobotsData());
            StartCoroutine(getBoxesData());
            StartCoroutine(getDropZoneData());
        }
    }

    IEnumerator getRobotsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(server + getRobots);
            yield return www.SendWebRequest();
    
            if (www.result != UnityWebRequest.Result.Success)
            {            
                Debug.Log(www.error);
            }
            else
            {

                robotsData = JsonUtility.FromJson<RobotsData>(www.downloadHandler.text);

                foreach(RobotData robot in robotsData.data)
                {
                    Vector3 newRobotPosition = new Vector3(robot.x, robot.y, robot.z);
                    // Debug.Log(newRobotPosition);

                    if(!robotsStarted)
                    {
                        prevPositions[robot.id] = newRobotPosition;
                        robots[robot.id] = Instantiate(robotPrefab, newRobotPosition, Quaternion.identity);

                        if(robot.has_box)
                        {
                            robots[robot.id].transform.GetChild(0).gameObject.SetActive(true);
                        }else
                        {
                            robots[robot.id].transform.GetChild(0).gameObject.SetActive(false);
                        }
                    }else
                    {
                        Vector3 currentPosition = new Vector3();
                        if(currPositions.TryGetValue(robot.id, out currentPosition))
                        {
                            prevPositions[robot.id] = currentPosition;
                        }
                        currPositions[robot.id] = newRobotPosition;

                        if(robot.has_box)
                        {
                            robots[robot.id].transform.GetChild(0).gameObject.SetActive(true);
                        }else
                        {
                            robots[robot.id].transform.GetChild(0).gameObject.SetActive(false);
                        }
                    }
                }
            }
            updated = true;
            if(!robotsStarted) robotsStarted = true;
    }

    IEnumerator getWallData()
    {
         UnityWebRequest www = UnityWebRequest.Get(server + getWall);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);

        else
        {
            wallsData = JsonUtility.FromJson<WallsData>(www.downloadHandler.text);

            foreach(WallData wall in wallsData.positions)
            {
                Instantiate(wallPrefab, new Vector3(wall.x, wall.y, wall.z), Quaternion.identity);
            }
        }
    }

    IEnumerator getBoxesData()
    {
        UnityWebRequest www = UnityWebRequest.Get(server + getBoxes);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }else
        {
            boxesData = JsonUtility.FromJson<BoxesData>(www.downloadHandler.text);

            foreach(BoxData box in boxesData.data)
            {
                if(!BoxesStarted)
                {
                    boxes[box.id] = Instantiate(boxPrefab, new Vector3(box.x, box.y, box.z), Quaternion.identity);

                }else
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
        }

        updated = true;
        if(!BoxesStarted) BoxesStarted = true;
    }

    IEnumerator getDropZoneData()
    {
        UnityWebRequest www = UnityWebRequest.Get(server + getDropZone);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            dropZoneData = JsonUtility.FromJson<DropZonesData>(www.downloadHandler.text);

            foreach(DropZoneData dropzone in dropZoneData.data)
            {
                if(!dropZoneStarted)
                {
                    dropzones[dropzone.id] = Instantiate(dropZonePrefab, new Vector3(dropzone.x, dropzone.y,dropzone.z), Quaternion.identity);
                    if (dropzone.numberBoxes == 0)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                }
                else
                {
                    if (dropzone.numberBoxes == 0)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);

                    }
                    else if (dropzone.numberBoxes == 1)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (dropzone.numberBoxes == 2)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (dropzone.numberBoxes == 3)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(false);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (dropzone.numberBoxes == 4)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (dropzone.numberBoxes== 5)
                    {
                        dropzones[dropzone.id].transform.GetChild(0).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(1).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(2).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(3).gameObject.SetActive(true);
                        dropzones[dropzone.id].transform.GetChild(4).gameObject.SetActive(true);
                    }
                }
            }

            updated = true;
            if(!dropZoneStarted) dropZoneStarted = true;
        }  
    }

    IEnumerator updateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(server + update);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(getRobotsData());
            StartCoroutine(getDropZoneData());
            StartCoroutine(getBoxesData());
        } 
    }

}

