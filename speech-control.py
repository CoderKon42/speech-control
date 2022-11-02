#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
import json
import subprocess

from vosk import Model, KaldiRecognizer

q = queue.Queue()
words = []
öffnen = False
last_command = ""


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    model = Model(lang="de")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(rec.Result())
                for word in words:
                    if word == "öffne" or word == "öffner": #frequently mistake (öffner)
                        öffnen = True
                last_command = ""
            else:
                vc = json.loads(rec.PartialResult())
                words = vc['partial'].split()
                print(words)

                for word in words:
                    if word == "öffne" or word == "öffner": #frequently mistake (öffner)
                        öffnen = True


                if öffnen:
                    for word in words:
                        if word == "firefox" and last_command != word:
                            subprocess.Popen(["/usr/bin/firefox", "startpage.com"])
                            last_command = word
                        if word == "schach" and last_command!= word:
                            subprocess.Popen(["/usr/bin/firefox", "lichess.org"])
                            last_command = word
                        if word == "youtube" and last_command!= word:
                            subprocess.Popen(["/usr/bin/firefox", "youtube.com"])
                            last_command = word
                        if word == "signal" and last_command!= word:
                            subprocess.Popen(["/usr/bin/signal-desktop"])
                            last_command = word
                        if word == "discord" and last_command!= word:
                            subprocess.Popen(["/usr/bin/discord"])
                            last_command = word
                        if word == "code" and last_command!= word:
                            subprocess.run(["flatpak", "run", "com.vscodium.codium"])
                            last_command = word
                        if word == "geogebra" and last_command!= word:
                            subprocess.Popen(["/usr/bin/geogebra"])
                            last_command = word
                        if word == "gimp" and last_command!= word:
                            subprocess.Popen(["/usr/bin/gimp"])
                            last_command = word
                        if word == "anki" and last_command!= word:
                            subprocess.run(["flatpak", "run", "net.ankiweb.Anki"])
                            last_command = word
                        if word == "github" and last_command!= word:
                            subprocess.Popen(["flatpak", "run", "io.github.shiftey.Desktop"])
                            last_command = word
                        if word == "whatsapp" or word == "whats-app" and last_command!= word:
                            subprocess.run(["flatpak", "run", "io.github.mimbrero.WhatsAppDesktop"])
                            last_command = word
                    öffnen = False
                
                
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
