#SingleInstance Force
FileEncoding("UTF-8")

Esc::ExitApp

~RAlt::Send('{Blind}{vkE8}')
>!r::print("hello")

print(str := "", end := "`n") {
    FileAppend(str . end, "*")
}