using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StateRobot : MonoBehaviour
{
    private bool currPickUp = false;

    public bool getPickUp()
    {
        return currPickUp;
    }
}
