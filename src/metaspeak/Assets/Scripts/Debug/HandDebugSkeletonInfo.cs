using UnityEngine;
using System.Collections;


public class HandDebugSkeletonInfo : MonoBehaviour
{
    [SerializeField]
    private OVRHand hand;

    [SerializeField]
    private OVRSkeleton handSkeleton;

    [SerializeField]
    private HandInfoFrequency handInfoFrequency = HandInfoFrequency.Once;

    private SocketQuest qs = new SocketQuest();

    private bool pauseDisplay = false;

    private void Awake()
    {
        if (!hand) hand = GetComponent<OVRHand>();
        if (!handSkeleton) handSkeleton = GetComponent<OVRSkeleton>();
    }

    public string Vector3ToString(Vector3 pos)
    {
        string result = "";
        result += pos.x;
        result += "|";
        result += pos.y;
        result += "|";
        result += pos.z;
        return result;
    }

    private void DisplayBoneInfo()
    {
        var boneArray = new ArrayList();
        var handType = handSkeleton.GetSkeletonType();
        boneArray.Add(handType.ToString());
        foreach (var bone in handSkeleton.Bones){
            boneArray.Add(bone.Id.ToString());
            Vector3 pos = bone.Transform.position;
            string pos_str = Vector3ToString(pos);
            boneArray.Add(pos_str);
        }

        // var printStr = "";
        //foreach (var name in boneArray)
        // {
        //     printStr += " " + name +"\n";
        // }

        qs.SendData(boneArray);

        /*
        foreach (var bone in handSkeleton.Bones)
        {
            Logger.Instance.LogInfo($"{handSkeleton.GetSkeletonType()}: boneId -> {bone.Id} pos -> {bone.Transform.position}");
        }

        Logger.Instance.LogInfo(handSkeleton.Bones.ToString());

        Logger.Instance.LogInfo($"{handSkeleton.GetSkeletonType()} num of bones: {handSkeleton.GetCurrentNumBones()}");
        Logger.Instance.LogInfo($"{handSkeleton.GetSkeletonType()} num of skinnable bones: {handSkeleton.GetCurrentNumSkinnableBones()}");
        Logger.Instance.LogInfo($"{handSkeleton.GetSkeletonType()} start bone id: {handSkeleton.GetCurrentStartBoneId()}");
        Logger.Instance.LogInfo($"{handSkeleton.GetSkeletonType()} end bone id: {handSkeleton.GetCurrentEndBoneId()}");
        */
    }
    
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space)) pauseDisplay = !pauseDisplay;

        if(hand.IsTracked && !pauseDisplay)
        {
            DisplayBoneInfo();
        }
    }

    public static void FirstMonitor(string message)
    {
        Logger.Instance.LogInfo(message);
    }

    public static void SecondMonitor(string message)
    {
        Logger2.Instance.LogInfo(message);
    }
}
