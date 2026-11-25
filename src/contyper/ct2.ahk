#Include JSON.ahk
#SingleInstance Force

FileEncoding("UTF-8")

>!Esc::ExitApp

~RAlt::Send('{Blind}{vkE8}')

print(str := "", end := "`n") {
    try {
        FileAppend(str . end, "*")
    }
}

join(arr, del := "") {
    outStr := ""
    for val in arr {
        outStr .= del . val
    }
    return SubStr(outStr, 1 + StrLen(del))
}

squish(arr) {
    finalArr := []
    for item in arr {
        if item is String {
            finalArr.Push item
        }
        else if item is Array {
            finalArr.Push(squish(item)*)
        }
    }
    return finalArr
}

parseHotkeyShorthand(str) {
    repMap := Map(
        "!", "Alt",
        "^", "Ctrl",
        "#", "Win",
        "+", "Shift",
        "<", "L",
        ">", "R"
    )
    for k, v in repMap {
        str := StrReplace(str, k, v)
    }
    return str
}

getFromIni(section, key) {
    return IniRead("core\options.ini", section, key)
}

class Ruleset {
    loops := []
    loopHotKeys := []
    lookOutKeys := []
    lastLayer := 1
    lastEntry := ""
    lastIndex := 1

    __New() {
        jFile := FileRead(A_ScriptDir . "\rs.json")
        this.loops := JSON.parse(jFile)
        this.getLayers()
        print "don getting layers"
        this.genHotkeys()
    }

    getLayers() {
        numLayers := getFromIni("Shortcuts", "layers")
        keycodes := StrSplit(getFromIni("Shortcuts", "keycodes"), ",")
        loop numLayers {
            print A_Index
            keybindBooleans := StrSplit(getFromIni("Shortcuts", A_Index - 1), ",")
            layerKeybinds := [">!"]
            for index, boolean in keybindBooleans {
                if boolean == "True" {
                    layerKeybinds.Push(keycodes[index])
                }
            }
            this.loopHotKeys.Push(layerKeybinds)
        }
        for layer in this.loopHotKeys {
            print "--" . join(layer, ", ")
        }
        this.lookOutKeys := squish(this.loopHotKeys)
    }

    step(entry, layer := 1) {
        for loop_ in this.loops {
            if loop_["layer"] + 1 = layer and loop_["entry"] = entry {
                actualLoop := loop_["loop"]
                if this.lastEntry = entry {
                    lastSymbol := actualLoop[this.lastIndex++]
                    this.lastIndex := Mod((this.lastIndex - 1), actualLoop.Length) + 1
                    heldModifiers := []
                    for modifier in this.lookOutKeys {
                        parsedModifier := parseHotkeyShorthand(modifier)
                        if GetKeyState(parsedModifier) {
                            heldModifiers.Push(parsedModifier)
                            Send "{" . parsedModifier . " up}"
                        }
                    }
                    Send "{Backspace " . StrLen(lastSymbol) . "}"
                    Send actualLoop[this.lastIndex]
                    for modifier in heldModifiers {
                        Send "{" . modifier . " up}"
                    }
                    return [lastSymbol, actualLoop[this.lastIndex]]
                }
                else {
                    this.lastEntry := entry
                    this.lastIndex := 1
                    this.lastLayer := 1
                    SendText actualLoop[this.lastIndex]
                    return ["", actualLoop[this.lastIndex]]
                }
            }
        }
    }

    genHotkeys() {
        for loop_ in this.loops {
            layer := Integer(loop_["layer"])
            print(loop_["entry"])
            hk := join(this.loopHotKeys[layer + 1]) . Format("sc{:03X}", GetKeySC(loop_["entry"]))
            Hotkey(
                hk,
                ((_, l, lyr) => this.step(l, lyr)).Bind(, loop_["entry"], layer + 1)
            )
        }
    }

    escapeLoop() {
        this.lastIndex := 1
        this.lastEntry := ""
        this.lastLayer := 1
    }
}

rs := Ruleset()

onEvent(hook, vk, sc) {
    d := false
    for layerModifiers in rs.loopHotKeys {
        p := true
        for modifier in layerModifiers {
            p := p and GetKeyState(parseHotkeyShorthand(modifier))
        }
        d := p or d
    }
    if not d {
        rs.escapeLoop()
    }
}

hook := InputHook("V")
hook.KeyOpt("{All}", "+N")
hook.OnKeyDown := onEvent
hook.OnKeyUp := onEvent
hook.Start

rsFile := FileRead(A_ScriptDir . "\rs.json")

loop {
    sleep 3000
    if rsFile != FileRead(A_ScriptDir . "\rs.json")
    {
        rsFile := FileRead(A_ScriptDir . "\rs.json")
        rs.__New()
        print("reload")
    }
}

~LButton::rs.escapeLoop()
~RButton::rs.escapeLoop()
~MButton::rs.escapeLoop()