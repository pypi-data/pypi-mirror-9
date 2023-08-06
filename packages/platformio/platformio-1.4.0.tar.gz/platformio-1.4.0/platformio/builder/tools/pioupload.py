# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join
from shutil import copyfile
from time import sleep

from SCons.Script import Exit
from serial import Serial

from platformio.util import get_logicaldisks, get_serialports


def FlushSerialBuffer(env, port):
    s = Serial(env.subst(port))
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def TouchSerialPort(env, port, baudrate):
    s = Serial(port=env.subst(port), baudrate=baudrate)
    s.setDTR(False)
    s.close()
    sleep(0.4)


def WaitForNewSerialPort(_, before):
    new_port = None
    elapsed = 0
    while elapsed < 10:
        now = [i['port'] for i in get_serialports()]
        diff = list(set(now) - set(before))
        if diff:
            new_port = diff[0]
            break

        before = now
        sleep(0.25)
        elapsed += 0.25

    if not new_port:
        Exit("Error: Couldn't find a board on the selected port. "
             "Check that you have the correct port selected. "
             "If it is correct, try pressing the board's reset "
             "button after initiating the upload.")

    return new_port


def AutodetectUploadPort(env):
    if "UPLOAD_PORT" in env:
        return

    if env.subst("$FRAMEWORK") == "mbed":
        msdlabels = ("mbed", "nucleo", "frdm")
        for item in get_logicaldisks():
            if (not item['name'] or
                    not any([l in item['name'].lower() for l in msdlabels])):
                continue
            print "Auto-detected UPLOAD_PORT/DISK: %s" % item['disk']
            env.Replace(UPLOAD_PORT=item['disk'])
            break
    else:
        for item in get_serialports():
            if "VID:PID" not in item['hwid']:
                continue
            print "Auto-detected UPLOAD_PORT: %s" % item['port']
            env.Replace(UPLOAD_PORT=item['port'])
            break

    if "UPLOAD_PORT" not in env:
        Exit("Error: Please specify `upload_port` for environment or use "
             "global `--upload-port` option.\n"
             "For the some development platforms it can be USB flash drive\n")


def UploadToDisk(_, target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()
    copyfile(join(env.subst("$BUILD_DIR"), "firmware.bin"),
             join(env.subst("$UPLOAD_PORT"), "firmware.bin"))
    print ("Firmware has been successfully uploaded.\n"
           "Please restart your board.")


def exists(_):
    return True


def generate(env):
    env.AddMethod(FlushSerialBuffer)
    env.AddMethod(TouchSerialPort)
    env.AddMethod(WaitForNewSerialPort)
    env.AddMethod(AutodetectUploadPort)
    env.AddMethod(UploadToDisk)
    return env
