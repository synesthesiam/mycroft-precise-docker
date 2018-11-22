FROM alpine:latest

RUN apk update && apk add --no-cache python3-dev build-base \
    py3-scipy portaudio-dev hdf5-dev py3-numpy py-numpy-dev

RUN pip3 install --no-cache-dir wheel

COPY /etc/tensorflow-1.8.0-cp36-cp36m-linux_x86_64.whl /
RUN pip3 install --no-cache-dir /tensorflow-1.8.0-cp36-cp36m-linux_x86_64.whl

RUN pip3 install --no-cache-dir pkgconfig cython
RUN pip3 install --no-cache-dir mycroft-precise