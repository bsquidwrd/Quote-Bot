FROM python:3.6.4-jessie


# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/

# Copy in your requirements file
ADD requirements.txt /requirements.txt
RUN python -m pip install -U pip
RUN pip install --no-cache-dir -r /requirements.txt

# Add code and volumes
ADD . /code/

# Add any custom, static environment variables needed by Django or your settings file here:
ENV CLIENT_ID=''
ENV CLIENT_TOKEN=''
ENV OWNER_ID='131224383640436736'
ENV DBOTS_KEY=''
ENV INVITE_URL=''
ENV LOG_CHANNEL=''

# Start Bot
CMD ["python", "/code/bot.py"]
