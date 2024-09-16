# Project Template

This is an example of how a project repo should be organized.

It contains several subdirectories that will contain standard elements of almost every project:

- `analysis`: This subdirectory will typically contain Python or R notebooks for making visualizations and statistical analyses. `/analysis/plots/` is the path to use when saving out `.pdf`/`.png` plots, a small number of which may be then polished and formatted for figures in a publication.
- `data`:  This subdirectory is where you put the raw and processed data from behavioral experiments and computational simulations. These data serve as input to `analysis`. *Important: Before pushing any csv files containing human behavioral data to a public code repository, triple check that these data files are properly anonymized. This means no bare Worker ID's.*
- `experiments`: If this is a project that will involve collecting human behavioral data, this is where you want to put the code to run the experiment. If this is a project that will involve evaluation of a computational model on a task, this is also where you want to put the task code (which imports the `model`).
- `model`: If this is a cognitive modeling project, this is where you want to put code for running the model. If this project involves training neural networks, you would put training scripts in here.

# Project documentation 

## Environment Setup

Gaze-contingent code in the Infant Learning Lab (as of Fall 2024) has some dependencies: 
- `tobii-research` package (dependant on python 3.10)
- `psychopy` package (python 3.10 as of 2022)
- `python-pygaze==0.7.6` (python>3)

To help with setup, I have created a python environment with all packages installed on the Dolphin booth in the main lab. This enviroment and the code should work cross-platform on Mac (non-M1 chip because of `tobii-research`) and PC if you wish to develop outside the lab. 

## Running the Code

### Dummy Mode

Toggle dummy mode = TRUE in the constants file

## Other notes

ALL audio, in video or otherwise, must have a sampling rate of 44100HZ. The following code using ffmpeg will convert any mp3 into 44100 sampling rate with 1 channel. 

```
for i in *-raw.mp3; do ffmpeg -i "$i" -ar 44100 -ac 1 "${i%-raw.mp3}.mp3"; done  
```

## Preregistration

Once we are in the later stages of desigining a new human behavioral experiment and preparing to run our first pilot, we will write up a pre-registration and either put it under version control within the project repo OR post it to the [Open Science Framework](https://osf.io/). We subscribe to the philosophy that ["pre-registrations are a plan, not a prison."](https://www.cos.io/blog/preregistration-plan-not-prison) They help us transparently document our thinking and decision-making process both for ourselves and for others, and will help us distinguish between confirmatory and exploratory findings. We do not believe that there is a single best way to write a pre-registration, but in many cases a more detailed plan will help us to clarify our experimental logic and set up our analyses accordingly (i.e., what each hypothesis predicts, which measures and analyses we will use to evaluate each relevant hypothesis). 

## Manuscripts 

When we are preparing to write up a manuscript (or a conference paper), we will start an [Overleaf](https://www.overleaf.com/) project. 
This is where you will want to place your LaTeX source `.tex` files for your paper and your publication-ready figures as high-resolution `.pdf` files in the `figures` directory. 
We typically format and fine-tune our figures using Adobe Illustrator.
