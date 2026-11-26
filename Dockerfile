FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    git \
    memcached \
    && apt-get clean

# Install Miniconda
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh && \
    bash /miniconda.sh -b -p $CONDA_DIR && \
    rm /miniconda.sh && \
    conda update -n base -c defaults conda

# Create the dev environment but do not activate by default
RUN conda create -n dev_env -c conda-forge python=3.11 redis-server=7.4.0 mongodb=6.0.16 mysql-server=9.0.1 && \
    conda clean --all --yes

RUN conda init

RUN echo "conda deactivate" >> /root/.bashrc

RUN mkdir /app/dbs

# Set working directory
WORKDIR /app

# Optional: copy your project files
COPY . /app

RUN pip3.11 install -r requirements.txt

# Default shell remains system bash, no conda activation
CMD ["tail", "-f", "/dev/null"]
