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
    public bool finished;

    public AgentData(string id, float x, float y, float z, bool finished)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.finished = finished;
    }
}

[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]
public class TrafficLightData
{
    public string id;
    public float x,y,z;
    public bool state;
    public bool vertical;
    public bool horizontal;

    public TrafficLightData(string id, float x, float y, float z,bool state, bool vertical, bool horizontal)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;
        this.vertical = vertical;
        this.horizontal = horizontal;
    }
}

[Serializable]
public class TrafficLightsData
{
    public List<TrafficLightData> positions;
    public TrafficLightsData() => this.positions = new List<TrafficLightData>();
}


public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getCarsEndpoint = "/getCars";
    string getPedestriansEndpoint = "/getPedestrians";
    string getTrafficLightsEndpoint = "/trafficLightState";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData carsData, pedestriansData;
    TrafficLightsData trafficLightData;
    Dictionary<string, GameObject> cars;
    Dictionary<string, GameObject> buses;
    Dictionary<string, GameObject> pedestrians;
    Dictionary<string, GameObject> lights;
    Dictionary<string, AgentData> carData;
    Dictionary<string, TrafficLightData> lightState;

    Dictionary<string, Vector3> carPrevPositions, carCurrPositions;
    Dictionary<string, Vector3> pedestrianPrevPositions, pedestrianCurrPositions;
    Dictionary<string, Vector3> lightsPositions;


    bool updated = false, started = false;

    public GameObject carPrefab, pedestriansPrefab, trafficLightPrefab;
    public int NumberCars, NumberPedestrians, NumberBuses;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        carsData = new AgentsData();
        pedestriansData = new AgentsData();
        trafficLightData = new TrafficLightsData();

        carPrevPositions = new Dictionary<string, Vector3>();
        carCurrPositions = new Dictionary<string, Vector3>();
        pedestrianPrevPositions = new Dictionary<string, Vector3>();
        pedestrianCurrPositions = new Dictionary<string, Vector3>();

        lightsPositions = new Dictionary<string, Vector3>();
        lightState = new Dictionary<string, TrafficLightData>();

        carData = new Dictionary<string, AgentData>();

        cars = new Dictionary<string, GameObject>();
        buses = new Dictionary<string, GameObject>();
        pedestrians = new Dictionary<string, GameObject>();
        lights = new Dictionary<string, GameObject>();
        
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

            foreach(var agent in carCurrPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = carPrevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                cars[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) cars[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                if (carData[agent.Key].finished) cars[agent.Key].SetActive(false);
                
            }
            foreach(var agent in pedestrianCurrPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = pedestrianPrevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                if (pedestrians[agent.Key]) pedestrians[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) pedestrians[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                
            }
            foreach(var agent in lightsPositions)
            {
                var redLight = lights[agent.Key].transform.Find("RedLight").gameObject;
                var greenLight = lights[agent.Key].transform.Find("GreenLight").gameObject;
                if (lightState[agent.Key].state == false)
                {
                    Debug.Log(agent.Key);
                    Debug.Log(lightState[agent.Key].state);
                    greenLight.SetActive(false);
                    redLight.SetActive(true);
                }
                if (lightState[agent.Key].state == true)
                {    
                    Debug.Log(agent.Key);
                    Debug.Log(lightState[agent.Key].state);
                    greenLight.SetActive(true);
                    redLight.SetActive(false);
                }
            }
            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
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
            StartCoroutine(GetCarsData());
            // StartCoroutine(GetBusesData());
            StartCoroutine(GetPedestriansData());
            StartCoroutine(GetTrafficLightData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NumberCars", NumberCars.ToString());
        form.AddField("NumberPedestrians", NumberPedestrians.ToString());
        form.AddField("NumberBuses", NumberPedestrians.ToString());

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
            StartCoroutine(GetCarsData());
            StartCoroutine(GetPedestriansData());
            StartCoroutine(GetTrafficLightData());
        }
    }


    IEnumerator GetCarsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getCarsEndpoint);

        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            carsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in carsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, 0.2f, agent.z);

                    if(!started)
                    {
                        carPrevPositions[agent.id] = newAgentPosition;
                        cars[agent.id] = Instantiate(carPrefab, newAgentPosition, Quaternion.identity);
                        carData[agent.id] = agent;
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if(carCurrPositions.TryGetValue(agent.id, out currentPosition))
                            carPrevPositions[agent.id] = currentPosition;
                        carCurrPositions[agent.id] = newAgentPosition;
                    }
            }
        }
    }

    IEnumerator GetPedestriansData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getPedestriansEndpoint);

        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            pedestriansData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in pedestriansData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, 0.2f, agent.z);

                    if(!started)
                    {
                        pedestrianPrevPositions[agent.id] = newAgentPosition;
                        pedestrians[agent.id] = Instantiate(pedestriansPrefab, newAgentPosition, Quaternion.identity);
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if(pedestrianCurrPositions.TryGetValue(agent.id, out currentPosition))
                            pedestrianPrevPositions[agent.id] = currentPosition;
                        pedestrianCurrPositions[agent.id] = newAgentPosition;
                    }
            }

        }
    }

    IEnumerator GetTrafficLightData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            trafficLightData = JsonUtility.FromJson<TrafficLightsData>(www.downloadHandler.text);
            foreach(TrafficLightData obstacle in trafficLightData.positions)
            {
                if (!started)
                {
                    lights[obstacle.id] = Instantiate(trafficLightPrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.Euler(0,-90,0));
                    lightsPositions[obstacle.id] = new Vector3(obstacle.x, obstacle.y, obstacle.z);
                    lightState[obstacle.id] = obstacle;
                }
                else
                {
                    lightState[obstacle.id] = obstacle;
                }
            }
            updated = true;
            if(!started) started = true;
        }
    }


}
