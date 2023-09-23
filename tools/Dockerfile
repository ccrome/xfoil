from alpine:3.18.3
RUN apk update
RUN apk add cmake make gfortran git musl-dev libx11-dev xvfb py3-pip py3-numpy py3-setuptools

RUN git clone https://github.com/ccrome/xfoil.git
RUN cd /xfoil && mkdir build && git checkout docker
RUN cd /xfoil/build && cmake  -Wno-dev ..
RUN cd /xfoil/build && make -j && make install

RUN cd /xfoil/tools && pip install .
ENV DISPLAY=:0

#CMD sh -c "(Xvfb :0 -screen 0 1024x768x16 &) && /usr/local/bin/xfoil"

RUN mkdir /tmp/serve
CMD sh -c "(Xvfb :0 -screen 0 1024x768x16 &) && cd /tmp/serve && airfoil-server"
