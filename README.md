# Oenomaus

> *No longer shall you be my Doctore. You will assume the mantle of lanista, and be warmly greeted by your name, Oenomaus.*

**A deep learning model to automatically detect anime-style images, using a convolutional neural network fine-tuned from ResNet18, implemented as a discord bot, which removes anime with deadly intent.**


<p align="center">
  <a href="https://example.com">
    <img src="https://raw.githubusercontent.com/dannyjameswilliams/oenomaus/main/example.gif" alt="Example Anime Removal">
  </a>
</p>

Oenomaus's true calling - not the doctore nor the lanista of the House of Batiatus, but the ever-vigilant destroyer of anime images. If you are tired of users posting anime within your discord server, take Oenomaus into your employment, and see anime vanquished.

## Features

### 🔎 Anime Detection 

Oenomaus is equipped with a deep learning model for image classification, fine-tuned from [ResNet18](https://pytorch.org/vision/master/models/generated/torchvision.models.resnet18.html) on a large dataset of anime and non-anime images. 
The size of this model is less than 50MB and the forward pass for predictions takes less than a second (on the CPU of a regular PC), and so is extremely fast. Simply specify the text channels you want Oenomaus to watch and he will detect any images or GIFs that
are anime. By default, if the probability of an image being anime is greater than 0.65, it will be removed. This is tunable via e.g. `!threshold 0.5`. Higher values of threshold will reduce false positives, which can happen if images are from other cartoons (non-anime), The Simpsons is a regrettable casualty.

### 🚫 Anime Removal

In a brutal fashion, Oenomaus's whip will smash apart the anime image that is detected, before removing it from the channel and issuing a warning to the user that posted it. Each time an anime image is detected, Oenomaus will create a GIF where his whip will slice
through the image. This generation takes around 5-10 seconds.

### 👋 New User Welcoming

When a new user joins the discord server, in a specified channel, Oenomaus will ask the user:
> What is beneath your feet?

For which he expects the reply:
> Sacred ground Doctore, watered with tears of blood.

If this reply is not given, the user is deemed unfit to be a gladiator, and removed from the server. Otherwise, they are assigned a new role within the discord server. (They must start as `new_role` and once they pass the test they are assigned `freshly-bought-slave`, configurable within `bot.py`).

## Installation

First, clone the github repository via
```bash
git clone https://github.com/dannyjameswilliams/oenomaus/
```
You must have Python installed, for which I used Python version 3.8.13, but later versions *should* work also. Provided you also have [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) installed, run
```bash
pip install -r requirements.txt
```
in the root directory to install all prerequisite packages. Then, create a file called `keys.py` in the root directory, with a single variable called `TOKEN` containing your [Discord API Token](https://discord.com/developers/docs/intro) to run the bot on. 
You must set up the bot within the [Discord Developer Portal](https://discord.com/developers/applications). 

## Usage

To activate the bot, run 
```bash
python bot.py
```
This will run Oenomaus locally in the terminal, and will continue to be run until it is closed. Alternatively, I have provided the `Dockerfile` within this repository so that you may set up a Docker container to run the python code, and also separately have an [Oenomaus Docker repository](https://hub.docker.com/repository/docker/dannyjameswilliams/oenomaus/general) on the Docker hub, which can be cloned and run completely independently of this repository.

To configure Oenomaus, there are a number of variables to tune within the top of `bot.py`, all commented detailing what they do. Most importantly, you should configure:
- `noanime_channels` to include all channels you would like Oenomaus to be monitoring and deleting anime images on, 
- `recruit_channel` to the channel name where Oenomaus will welcome new recruits,
- `new_role` to the name of the Discord role (which I recommend has zero permissions except for writing in `recruit_channel`) all new members will have,
- `recruit_role` to the name of the Discord role for those who pass the welcoming test (e.g. this can give them the regular server role),
- `exempt_role` to the name of the Discord role which is exempt from Oenomaus's gaze, and is free to post any images they would like.















