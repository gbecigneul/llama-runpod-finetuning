FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

RUN apt-get update && \
    apt-get install -y git \
                       build-essential \
                       && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ggerganov/llama.cpp
WORKDIR /llama.cpp
RUN make LLAMA_CUBLAS=1

RUN mkdir models/
COPY /workspace /llama.cpp/models/

RUN pip install runpod

ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1

CMD ["/bin/bash"]