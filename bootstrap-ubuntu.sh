export PROJECT=${PROJECT:-glfw-cffi}
export PROJECT_HOME=${PROJECT_HOME:-/opt/$PROJECT/}
export WORKON_HOME=${WORKON_HOME:-/root/.local/envs}
export GLFW_VERSION=${GLFW_VERSION:-3.2.1}
export DISPLAY=${DISPLAY:-:99.0}
export GLFW_LIBRARY=${GLFW_LIBRARY:-/root/lib/libglfw.so}

mkdir -p $PROJECT_HOME \
  && mkdir -p $WORKON_HOME \
  && apt-get update -qq \
  && apt-get install -qq software-properties-common lsb-release wget unzip \
  && export RELEASE_NAME=$(lsb_release -cs) \
  && add-apt-repository "deb http://us.archive.ubuntu.com/ubuntu/ $RELEASE_NAME main restricted universe multiverse" \
  && add-apt-repository "deb http://us.archive.ubuntu.com/ubuntu/ $RELEASE_NAME-updates main restricted universe multiverse" \
  && apt-get update -qq \
  && DEBIAN_FRONTEND=noninteractive apt-get install -qq \
    apt-utils \
    autogen \
    automake \
    bash \
    bc \
    bison \
    build-essential \
    bzip2 \
    ca-certificates \
    cmake \
    curl \
    file \
    flex \
    freeglut3-dev \
    g++ \
    gcc \
    git \
    gzip \
    libghc-x11-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libglu1-mesa-dev \
    libxcursor-dev \
    libxi-dev \
    libxrandr-dev \
    libxxf86vm-dev \
    make \
    menu \
    mesa-common-dev \
    ncurses-dev \
    pkg-config \
    python \
    python-pip \
    rsync \
    runit \
    sed \
    sudo \
    tar \
    vim \
    wget \
    xinit \
    xorg-dev \
    xvfb \
    xz-utils \
  && python -m pip install --upgrade pip vex \
  && wget -O glfw.zip https://github.com/glfw/glfw/releases/download/$GLFW_VERSION/glfw-$GLFW_VERSION.zip \
  && unzip glfw.zip \
  && cd glfw-$GLFW_VERSION \
  && cmake -DBUILD_SHARED_LIBS=ON -DGLFW_BUILD_EXAMPLES=OFF -DGLFW_BUILD_TESTS=OFF -DGLFW_BUILD_DOCS=OFF -DCMAKE_INSTALL_PREFIX=$HOME \
  && make \
  && make install \
  && cd .. \
  && apt-get -y clean
