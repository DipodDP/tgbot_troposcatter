# Use an official Python runtime as a parent image
FROM python:3.10-buster

# Set the working directory in the container
WORKDIR /usr/src/app

# Install poetry
RUN pip install poetry

# Copy the poetry lock and pyproject files to the container
COPY poetry.lock pyproject.toml /usr/src/app/
COPY . /usr/src/app/

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Command to run the bot
CMD ["python", "bot.py"]