﻿using System;
using Neuro.Events;
using Neuro.Minigames;
using Neuro.Utilities;
using Reactor.Utilities.Attributes;
using UnityEngine;

namespace Neuro.Interactions;

[RegisterInIl2Cpp, ShipStatusComponent]
public sealed class InteractionsHandler : MonoBehaviour
{
    public static InteractionsHandler Instance { get; private set; }

    public InteractionsHandler(IntPtr ptr) : base(ptr)
    {
    }

    private void Awake()
    {
        if (Instance)
        {
            NeuroUtilities.WarnDoubleSingletonInstance();
            Destroy(this);
            return;
        }

        Instance = this;
    }

    public void UseTarget(IUsable usable)
    {
        if (MeetingHud.Instance || Minigame.Instance || usable == null) return;

        // TODO: Allow neural network to specifiy intention of interacting with usables
        switch (usable.Il2CppCastToTopLevel())
        {
            case Console console:
                UseConsole(console);
                break;

            case DeconControl decon:
                decon.Use();
                break;

            case DoorConsole door:
                door.Use();
                break;

            // case Ladder ladder:
            //     break;

            // case MapConsole admin:
            //     break;

            // case OpenDoorConsole simpleDoor:
            //     break;

            // case PlatformConsole platform:
            //     break;

            // case SystemConsole system:
            //     break;

            // case Vent vent:
            //     break;
        }
    }

    public void UseConsole(Console console)
    {
        PlayerTask task = console.FindTask(PlayerControl.LocalPlayer);
        if (task == null)
        {
            Warning($"Unable to find task from console id {console.ConsoleId}");
            return;
        }
        Minigame minigame = task.GetMinigamePrefab();

        if (MinigameHandler.ShouldOpenConsole(console, minigame, task))
        {
            console.Use();
        }
        else
        {
            Warning($"Shouldn't open console id {console.ConsoleId} for minigame {task.GetMinigamePrefab().GetIl2CppType().Name}");
        }
    }
}
