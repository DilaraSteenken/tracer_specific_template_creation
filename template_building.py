############################################## create an average template based on baseline images #############################################
# in this script we loop through all the project folders and select the baseline scans, then average them and apply smoothing
# in this way we can crate a mask based on borders of the template and automatically crop the brain images once they are in the tracer space

# load packages
import os
import sys

import ants
import numpy as np
import pandas as pd
import re
import openpyxl as xl
from nilearn import image
import nilearn
import nibabel as nib
from nilearn import image, plotting
from matplotlib import pyplot as plt
from pathlib import Path
import yaml

################################################################################################################
# loading working directory
project_dir = Path(r"/home/user/dsteenken/PycharmProjects/tracer_specific_template/")
config_path = project_dir / "config_local.yml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["template_building"]
## define folders
main_folder = settings["main_folder"] # replace with your directory
sub_folder = 'raw'
sub_folder_derivatives = 'derivatives'
sub_folder_preproc = 'preproc'
df = pd.read_excel(os.path.join(main_folder, 'mediso_data_summary.xlsx')) ## load data table
images = [] # an empty array to save the images
tracer = 'ucbh' # define tracer

################################################################################################################
## loop through data table
for idx, row in df.iterrows():
    project = row['project']
    session = row['session']
    tracer = row['tracer']
    subject = row['subject']
    if session == 'ses-Baseline' and tracer == tracer: # pay attention whether ucbh or fdg!
        filename_pet = row['filename_pet'] # baseline filename
        pet_reg_filename = re.sub('rec-stat', 'pet-reg_rec-stat', filename_pet, flags=re.IGNORECASE) # rename as pet registered
        img = os.path.join(main_folder, sub_folder_derivatives, sub_folder_preproc, project, subject, session, 'pet', pet_reg_filename) # reg pet image
        print(f'pet registered image: {img}')
        if os.path.exists(img):
            images.append(img)
        else:
            print(f'No image {img}')
len(images)
############################# average pet registered images ######################
avg_img = ants.average_images(images, normalize=False)
# save the averaged image
averaged_image_dir = settings["averaged_image_dir"]
averaged_image = os.path.join(averaged_image_dir, f'baseline_{tracer}_avg.nii.gz')
ants.image_write(avg_img, averaged_image) # pay attention fdg or ucbh!
########################### template smoothing gaussian filter 0.4 ###############
# load average image fdg or ucbh!
averaged_image_dir = settings["averaged_image_dir"]
averaged_image = os.path.join(averaged_image_dir, f'baseline_{tracer}_avg.nii.gz')
avg_img = nib.load(averaged_image)
smoothed_img = nilearn.image.smooth_img(avg_img,0.4)
smoothed_image = os.path.join(averaged_image_dir, f'baseline_{tracer}_template.nii.gz')
nib.save(smoothed_img, smoothed_image) # fdg or ucbh!!
################################# visualise #####################################
plotting.plot_anat(smoothed_img, display_mode='ortho', cut_coords=None, annotate=True, draw_cross=False, radiological=False)
plt.show()
