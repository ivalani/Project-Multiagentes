using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RobotAction : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private float boxRange = 0.5f;
    private GameObject box;
    private Vector3[] raycastDirections;
    bool pickUpBox = false;
    private RaycastHit hit;
    
    // Start is called before the first frame update
    void Start()
    {
        raycastDirections = new[] {Vector3.forward, Vector3.back, Vector3.left, Vector3.right}; 
        
    }

    // Update is called once per frame
    void Update()
    {
        foreach(var raycastDirection in raycastDirections)
        {
            if (Physics.Raycast(transform.position, raycastDirection, out hit, boxRange))
            {
                if (hit.collider.gameObject)
                {
                    
                }
            }
        }
    }
}
