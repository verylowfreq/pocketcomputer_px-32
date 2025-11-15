import editor

try:
    editor.main(True)

except Exception as e:
    print(e)
    machine.soft_reset()

