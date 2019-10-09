# Dockerfile for the FAPS API application.
#
# 'docker-compose build' from the parent directory will build this.
# 'docker-compose up' will too, if it needs to be.
#
# To build this by hand, cd into the "consumer" directory and run
# 'docker build -t fapsapplicationService .', and then you can manually run
# 'docker run --rm -e AMQP_URL=... consumer' to run it.

# This is based on the Python 2.7 Alpine Linux image.  See
# https://hub.docker.com/_/python/ for details on this image.
FROM yoanlin/opencv-python3:latest

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# Actually install the application
WORKDIR /usr/src/app
# It's only a single file.  It has to be in the same directory as the
# Dockerfile, or a subdirectory, but not a parent or sibling.
COPY . .

# Install dependencies.
RUN pip install -r requirements.txt

# When you just 'docker run publisher' with no command afterwards,
# default to this:
CMD ["python", "FAPSApplicationService.py"]