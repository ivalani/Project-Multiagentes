using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StateBox : MonoBehaviour
{
    [SerializeField] MeshRenderer meshRenderer;
    private bool pickUp;
    private bool dropOff;
    // Start is called before the first frame update
    void Start()
    {
        Invisible(false);
        
    }

    public void Invisible(bool invisible)
    {
        if (!invisible)
        {
            dropOff = true;
        }
        meshRenderer.enabled = !invisible;
    }

    public bool getPickUp()
    {
        return pickUp;
    }

    public bool getDropOff()
    {
        return dropOff;
    }
}
