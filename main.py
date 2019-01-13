#!/usr/bin/env python3
import os
import io
import json
import wave
import argparse
import subprocess
import threading
import logging
logging.basicConfig(level=logging.DEBUG)

from precise_runner import PreciseEngine, PreciseRunner
import paho.mqtt.client as mqtt

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='mycroft-precise')
    parser.add_argument('--host',
                        help='MQTT host (default=localhost)',
                        type=str, default='localhost')

    parser.add_argument('--port',
                        help='MQTT port (default=1883)',
                        type=int, default=1883)

    parser.add_argument('--site-id', help='Hermes siteId (default=default)',
                        type=str, default='default')

    parser.add_argument('--wakeword-id', help='Hermes wakewordId (default=default)',
                        type=str, default='default')

    parser.add_argument('--model',
                        type=str,
                        required=True,
                        help='Path to model file (.pb)')

    parser.add_argument('--sensitivity',
                        help='Model sensitivity (default=0.5)',
                        type=float,
                        default=0.5)

    parser.add_argument('--trigger-level', help='Number of trigger events required (default=3)',
                        type=int, default=3)

    parser.add_argument('--feedback', help='Show printed feedback', action='store_true')
    args = parser.parse_args()

    topic_audio_frame = 'hermes/audioServer/%s/audioFrame' % args.site_id
    topic_hotword_detected = 'hermes/hotword/%s/detected' % args.wakeword_id

    # Create runner
    engine = PreciseEngine('precise-engine', args.model)
    stream = ByteStream()

    client = mqtt.Client()
    first_frame = True

    def on_activation():
        nonlocal first_frame
        if args.feedback:
            print('!', end='', flush=True)

        logging.debug('Hotword detected!')
        payload = json.dumps({
            'siteId': args.site_id,
            'modelId': args.model,
            'modelVersion': '',
            'modelType': 'personal',
            'currentSensitivity': args.sensitivity
        }).encode()

        client.publish(topic_hotword_detected, payload)
        first_frame = True

    runner = PreciseRunner(engine, stream=stream,
                            sensitivity=args.sensitivity,
                            trigger_level=args.trigger_level,
                            on_activation=on_activation)

    # Set up MQTT
    def on_connect(client, userdata, flags, rc):
        client.subscribe(topic_audio_frame)
        logging.debug('Connected to %s' % args.host)

    def on_message(client, userdata, message):
        nonlocal first_frame
        try:
            if message.topic == topic_audio_frame:
                if first_frame:
                    logging.debug('Receiving audio data')
                    first_frame = False

                if args.feedback:
                    print('.', end='', flush=True)

                # Extract audio data
                with io.BytesIO(message.payload) as wav_buffer:
                    with wave.open(wav_buffer, mode='rb') as wav_file:
                        audio_data = wav_file.readframes(wav_file.getnframes())
                        stream.write(audio_data)
        except Exception as e:
            logging.exception('on_message')

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port)

    runner.start()

    try:
        logging.info('Listening')
        client.loop_forever()
    except KeyboardInterrupt:
        pass

    try:
        stream.close()
        runner.stop()
    except:
        pass

# -----------------------------------------------------------------------------

class ByteStream:
    def __init__(self):
        self.buffer = bytes()
        self.event = threading.Event()
        self.closed = False

    def read(self, n=-1):
        # Block until enough data is available
        while len(self.buffer) < n:
            if not self.closed:
                self.event.wait()
            else:
                self.buffer += bytearray(n - len(self.buffer))

        chunk = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return chunk

    def write(self, data):
        if self.closed:
            return

        self.buffer += data
        self.event.set()

    def close(self):
        self.closed = True
        self.event.set()

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
