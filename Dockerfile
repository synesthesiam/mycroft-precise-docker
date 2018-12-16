FROM homeassistant/amd64-base:latest

# Install system packages
RUN apk update && apk add --no-cache python3-dev build-base \
    py3-scipy portaudio-dev py3-numpy py-numpy-dev

# Add edge repo
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/main' > /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories

# Install system packages
RUN apk update && apk add --no-cache hdf5-dev

RUN pip3 install --no-cache-dir wheel

# Install tensorflow
COPY /etc/tensorflow-1.8.0-cp36-cp36m-linux_x86_64.whl /
RUN pip3 install --no-cache-dir /tensorflow-1.8.0-cp36-cp36m-linux_x86_64.whl

# Install Mycroft Precise
RUN pip3 install --no-cache-dir pkgconfig cython
RUN pip3 install --no-cache-dir mycroft-precise==0.2.0

# Add random sounds for training
COPY etc/pbsounds /pbsounds

# Need arecord
RUN apk add --no-cache alsa-utils

# Patch precise runner to use acrecord instead of PyAudio
COPY src/precise_runner/runner.py /usr/lib/python3.6/site-packages/precise_runner/
COPY src/precise/scripts/listen.py /usr/lib/python3.6/site-packages/precise/scripts/