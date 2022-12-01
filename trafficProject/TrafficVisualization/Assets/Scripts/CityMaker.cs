using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject destinationPrefab;
    [SerializeField] GameObject buildingPrefab;
    [SerializeField] GameObject trafficLightPrefab;
    [SerializeField] GameObject sideWalkPrefab;
    [SerializeField] GameObject pedestrianCrossing;
    [SerializeField] int tileSize;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length - 2;
        Debug.Log(y);

        Vector3 position;
        GameObject tile;

        for (int i=0; i<tiles.Length; i++) {
            // Creates right or left road
            if (tiles[i] == '>' || tiles[i] == '<') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            // Creates up or down road
            } else if (tiles[i] == 'v' || tiles[i] == '^') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if(tiles[i] == '+')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } 
            else if (tiles[i] == 's') {
                // Creates trafficLight
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                tile = Instantiate(trafficLightPrefab, position, Quaternion.Euler(0,180,0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'S') {
                // Creates trafficLight
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                tile = Instantiate(trafficLightPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'D') {
                // Creates destination
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(destinationPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                tile = Instantiate(sideWalkPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
     
                x += 1;
            } else if (tiles[i] == '#') {
                // Creates building
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab, position, Quaternion.identity);
                tile.transform.localScale = new Vector3(0.5f, Random.Range(0.5f, 2.0f), 0.5f);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'B'){
                // Creates sidewalk
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(sideWalkPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } 
            else if (tiles[i] == 'Z'){
                // Creates pedestrian crossing
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(pedestrianCrossing, position, Quaternion.Euler(0, 0, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'z'){
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(pedestrianCrossing, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '\n') {
                x = 0;
                y -= 1;
            }
        }

    }
}
