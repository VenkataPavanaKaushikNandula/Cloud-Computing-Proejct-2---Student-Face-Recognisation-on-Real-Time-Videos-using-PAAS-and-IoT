ARG FUNCTION_DIR="/home/ubuntu/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

#------------------------------STAGE 1--------------------------------
FROM python:${RUNTIME_VERSION} AS python-alpine

RUN apt-get update \
    && apt-get install -y cmake ca-certificates libgl1-mesa-glx
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip
RUN apt-get install libhdf5-dev -y
RUN apt-get install libhdf5-serial-dev
RUN apt-get install libatlas-base-dev -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
#------------------------------STAGE 2--------------------------------
FROM python-alpine AS build-image
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
RUN mkdir -p ${FUNCTION_DIR}
ADD ./CSE546_2022Spring_Project2 ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install matplotlib --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install requests --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install torch==1.10.2+cpu torchvision==0.11.3+cpu torchaudio==0.10.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install boto3 --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install opencv-python --target ${FUNCTION_DIR}
#------------------------------STAGE 3--------------------------------
FROM python-alpine
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD ["eval_face_recognition.handler"]