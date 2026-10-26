########################################## pet registered to ct #######################################################
# in this script we rigidly register the pet images to their corresponding ct images
# import packages
import pandas as pd
import numpy as np
import ants
import os
import warnings
import openpyxl as xl
import re
import nibabel as nib
from nilearn import image, plotting
from matplotlib import pyplot as plt
from pathlib import Path
import yaml

################################################################################################################
# loading working directory
project_dir = Path(r"/home/user/dsteenken/PycharmProjects/tracer_specific_template")
config_path = project_dir / "config_local.yml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["pet_2_ct"]
## define folders
main_folder = settings["main_folder"] # replace with your directory
# these should be the same if in bids format
sub_folder = 'raw' # where raw data is
sub_folder_derivatives = 'derivatives' # where the preprocessed data and the other infos are going to be
sub_folder_preproc = 'preproc' # preprocessed data is saved
## load data table
df = pd.read_excel(os.path.join(main_folder, 'mediso_data_summary.xlsx')) # load your data table with your name

##############################################################################################################
# if you have the data table and all the info in it you can loop through the table
for idx, row in df.iterrows(): # here loops through each row

    project = row['project'] # takes each project name if several projects exist otherwise just the one you have
    subject = row['subject'] # takes each subject
    session = row['session'] # takes each session
    tracer = row['tracer'] # takes each tracer if you have multiple tracers
    filename_pet = row['filename_pet'] # you should have the filenames on the data table, it will take it from there
    filename_ct = row['filename_ct'] # same for ct file names
    pet = row['pet'] # checks if pet existing, if exists 1 on data table if not 0
    ct = row['ct'] # checks for ct files

    if pet == 1 and ct == 1: # if both pet and ct exist we load the images

        fixed_img = os.path.join(main_folder, sub_folder, project, subject, session, 'ct', filename_ct) # ct is the fixed image because we always register the pet to the ct
        print(f'Fixed: {fixed_img}') # you can print the name to double-check if you want or comment out
        moving_img = os.path.join(main_folder, sub_folder, project, subject, session, 'pet', filename_pet) # pet is the moving image and the pet is moved to be registred to the ct
        print(f'Moving: {moving_img}') # again you can either print the name or comment out

        # loading images
        if os.path.exists(fixed_img) and os.path.exists(moving_img): # check if the files exist
            try: # if they exist it will try to load and register them, if not it will show a warning and keep going with the next images

                fixed = ants.image_read(fixed_img) # load the ct image
                moving = ants.image_read(moving_img) # load the pet image

                output_dir = os.path.join(main_folder, sub_folder_derivatives, sub_folder_preproc, project, subject, session, 'pet')  # create the output folder name for the registered image to be saved
                os.makedirs(output_dir, exist_ok=True) # create the actual folder

                ct_reg_filename = re.sub('rec-stat', 'ct-reg_rec-stat', filename_pet, flags=re.IGNORECASE) # here you take the raw pet file name and replace it with "ct-reg_rec-stat"
                output_file = os.path.join(output_dir, ct_reg_filename) # create a file name for the output data to be saved

                reg = ants.registration(fixed=fixed, moving=moving, type_of_transform='Rigid') # register the moving image to the fixed image
                ants.image_write(reg['warpedmovout'], filename=output_file) # you take the registered image out and save it with the newly defined name
                print(f'Registered: {output_file}') # print the name of the registered image

                # display the registered images
                if os.path.exists(output_file): # check if the registered image exist
                    pet_img = nib.load(output_file)  # load the registered pet image

                    plotting.plot_anat(pet_img, title=f'{ct_reg_filename}', display_mode='ortho', cut_coords=None, annotate=True, draw_cross=False, radiological=False) # visualise the image
                    plt.show()
                else:
                    print(f"No file: {output_file}")
            except Exception as e: # it prints e if it could not load and register the files
                print(e)
        else: # if the pet or the ct do not exist, nothing is done
            print(f'{fixed_img} or {moving_img} not found')

