FROM pytorch/pytorch


RUN apt update && apt install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
		vim \
		sudo \
		graphviz \
		ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy

WORKDIR /
ENV OPENCV_VERSION="4.1.1"
RUN wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
&& unzip ${OPENCV_VERSION}.zip \
&& mkdir /opencv-${OPENCV_VERSION}/cmake_binary \
&& cd /opencv-${OPENCV_VERSION}/cmake_binary \
&& cmake -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DCMAKE_INSTALL_PREFIX=$(python3.7 -c "import sys; print(sys.prefix)") \
  -DPYTHON_EXECUTABLE=$(which python3.7) \
  -DPYTHON_INCLUDE_DIR=$(python3.7 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON_PACKAGES_PATH=$(python3.7 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
  .. \
&& make install \
&& rm /${OPENCV_VERSION}.zip \
&& rm -r /opencv-${OPENCV_VERSION}


RUN pip install --no-cache-dir https://github.com/PytorchLightning/pytorch-lightning/archive/master.zip --upgrade
RUN pip install --no-cache-dir \
	pandas \
	notebook\
	jupyterlab\
	scikit-image \
	scikit-learn \
	scipy \
	tensorboard \
	pillow \
	dask \
	flask \
	ipywidgets \
	cython \
	numba \
	facenet-pytorch \
	mmcv \
	imutils\
	albumentations

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt update && apt install -y \
	nodejs \
	npm \
	yarn

RUN mkdir /home/kommiu

RUN cgroupadd  -r -g 1000 kommiu && \
	useradd -r -g 1000 -u 1000 kommiu -d /home/kommiu/ 

ENV HOME=/home/kommiu
ENV APP_HOME=/home/kommiu/app

RUN mkdir $APP_HOME

ADD .profile $HOME


WORKDIR /home/kommiu/app
USER kommiu
