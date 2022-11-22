using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData{
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z){
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}
[Serializable]
public class AgentsData{
    public List<AgentData> positions;
    public AgentsData() => this.positions = new List<AgentData>();
}

public class RobotMovement : MonoBehaviour
{
    string serverURL = "http://localhost:8000";
    string getRobots = "/getRobots";
    string getWall = "/getWall";
    string setConfig = "/init";
    string update = "/update";
    AgentsData robotsData, wallData;
    Dictionary<string, GameObject> robots;
    Dictionary<string, Vector3> previousPosition, currentPosition;

    bool updated = false, started = false;

    public GameObject robotPrefab, wallPrefab, floor;
    public int NumberRobots, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        robotsData = new AgentsData();
        wallData = new AgentsData();

        previousPosition = new Dictionary<string, Vector3>();
        currentPosition = new Dictionary<string, Vector3>();

        robots = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);

        timer = timeToUpdate;

        StartCoroutine(setConfiguration());
    }
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
            dt = 1.0f - (timer/timeToUpdate);

            foreach (var agent in currentPosition)
            {
                Vector3 currPosition = agent.Value;
                Vector3 prevPosition = previousPosition[agent.Key];

                Vector3 interpolated = Vector3.Lerp(prevPosition, currPosition, dt);
                Vector3 direction = currPosition - interpolated;

                robots[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) robots[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }
    IEnumerator updateSimulation(){
        UnityWebRequest www = UnityWebRequest.Get(serverURL + update);
        yield return www.SendWebRequest();

        if(www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
            StartCoroutine(getRobotsData());
    }
    IEnumerator setConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NumberAgents", NumberRobots.ToString());
        form.AddField("CanvasWidth", width.ToString());
        form.AddField("CanvasHeight", height.ToString());
        form.AddField("NumberBoxes", 0.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverURL + setConfig, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if(www.result != UnityWebRequest.Result.Success){
            Debug.Log(www.error);
        }else
        {
            Debug.Log("Configuration uploaded!");
            Debug.Log("Getting agents positions");
            StartCoroutine(getRobotsData());
            StartCoroutine(getWallData());
        }
    }
    IEnumerator getRobotsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverURL + getRobots);

        yield return www.SendWebRequest();

        if(www.result != UnityWebRequest.Result.Success){
            Debug.Log(www.error);
        }else{
            robotsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData robot in robotsData.positions){

                Vector3 newRobotPosition = new Vector3(robot.x, robot.y, robot.z);

                if(!started){

                    previousPosition[robot.id] = newRobotPosition;
                    robots[robot.id] = Instantiate(robotPrefab, newRobotPosition, Quaternion.identity);
                }else
                {
                    Vector3 currPosition = new Vector3();
                    if(currentPosition.TryGetValue(robot.id, out currPosition))
                        previousPosition[robot.id] = currPosition;
                    currentPosition[robot.id] = newRobotPosition;
                }
            }

            updated = true;
            if(!started) started = true;
        }
    }
    IEnumerator getWallData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverURL + getWall);
        yield return www.SendWebRequest();

        if(www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            wallData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(wallData.positions);

            foreach(AgentData wall in wallData.positions)
            {
                Instantiate(wallPrefab, new Vector3(wall.x, wall.y, wall.z), Quaternion.identity);
            }
        }
    }
}
