FROM python:3.9-slim-buster

LABEL maintainer="techops@ona.io"

# Create a group and user for UReport:
ARG UREPORT_USER=ureport
RUN groupadd -r ${UREPORT_USER} \
  && useradd -r -g ${UREPORT_USER} ${UREPORT_USER}

ARG UREPORT_VERSION

ENV UREPORT_VERSION=${UREPORT_VERSION} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.1.5 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin"

# Install run deps:
RUN set -ex \
  && RUN_DEPS=" \
  postgresql-client \
  wget \
  vim \
  binutils \
  libproj-dev \
  gdal-bin \
  git \
  " \
  && apt-get update \
  && apt-get install -y --no-install-recommends $RUN_DEPS \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /ureport

# Download UReport release:
RUN echo "Downloading UReport ${UREPORT_VERSION} from https://github.com/rapidpro/ureport/archive/${UREPORT_VERSION}.tar.gz" \
  && wget -O ureport.tar.gz "https://github.com/rapidpro/ureport/archive/${UREPORT_VERSION}.tar.gz" \
  && tar -xf ureport.tar.gz --strip-components=1 \
  && rm ureport.tar.gz

COPY requirements.txt /requirements.txt

# Install build deps:
RUN set -ex \
  && BUILD_DEPS=" \
    build-essential \
    curl \
    libpq-dev \
  " \
  && apt-get update \
  && apt-get install -y --no-install-recommends $BUILD_DEPS \
  # install poetry
  && curl -sSL 'https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py' | python \
  && poetry --version \
  && poetry install --no-dev \
  && pip install --no-cache-dir -r /requirements.txt \
  # install nodejs
  && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
  && apt-get install -y nodejs \
  # install less and coffeescript
  && npm install -g coffeescript less \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
  && rm -rf /var/lib/apt/lists/*

COPY settings.py /ureport/ureport/
COPY uwsgi.ini /ureport/

RUN mkdir /ureport/sitestatic

COPY docker-entrypoint.sh /

# Set up proper permissions:
RUN chmod +x '/docker-entrypoint.sh' \
  && chown ${UREPORT_USER}:${UREPORT_USER} -R /ureport

EXPOSE 3031

ENV DJANGO_SETTINGS_MODULE=ureport.settings

USER ${UREPORT_USER}

ENTRYPOINT [ "/docker-entrypoint.sh" ]
