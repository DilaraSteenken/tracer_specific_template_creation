########################################## registering ct registered pet images to a single image ###############
# # in this script we rigidly register the the ct registered pet images to a selected pet image (that has a good outlie) so that all images are more less in the same space
# if we want to create a fdg temple we use aa fdg image, if ucbh template then use a ucbh image

# import packages
import numpy as np
import ants
import os
import warnings
import openpyxl as xl
import re
import pandas as pd
import nibabel as nib
from nilearn import image, plotting
from matplotlib import pyplot as plt
from pathlib import Path
import yaml

##############################################################################################################
# loading working directory
project_dir = Path(r"/home/user/dsteenken/PycharmProjects/tracer_specific_template/")
config_path = project_dir / "config_local.yml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["main_dir"]
## define folders
main_folder = settings["main_folder"] # replace with your directory
## define folders
main_folder = settings["main_folder"] # replace with your directory
sub_folder = 'raw'
sub_folder_derivatives = 'derivatives'
sub_folder_preproc = 'preproc'
## load data table
df = pd.read_excel(os.path.join(main_folder, 'mediso_data_summary.xlsx'))

##############################################################################################################
# fixed is a single pet image
fixed_img = settings["fixed_img"]
print(f'Fixed: {fixed_img}')

##############################################################################################################
# loop over each row
for idx, row in df.iterrows():
    project = row['project']
    session = row['session']
    tracer = row['tracer']
    subject = row['subject']
    if session == 'ses-Baseline' and tracer == 'ucbh': # if the single image is fdg use fdg otherwise ucbh tracer
        filename_pet = row['filename_pet']
        filename_ct = row['filename_ct']
        pet = row['pet']
        ct = row['ct']
        # if ct exists then use the ct registered pt image if not use the raw pet image
        if pet == 1 and ct == 1: # if both pet and ct exist load the images
            ct_reg_filename = re.sub('rec-stat', 'ct-reg_rec-stat', filename_pet, flags=re.IGNORECASE)
            moving_img = os.path.join(main_folder, sub_folder_derivatives, sub_folder_preproc, project, subject, session, 'pet', ct_reg_filename) # moving is pet
            print(f'Moving: {moving_img}')
        elif pet == 1 and ct == 0:
            moving_img = os.path.join(main_folder, sub_folder, project, subject, session, 'pet', filename_pet) # moving is pet
            print(f'Moving: {moving_img}')
        # loading images
        if os.path.exists(fixed_img) and os.path.exists(moving_img):
            try:
                fixed = ants.image_read(fixed_img)
                moving = ants.image_read(moving_img)

                # create the output folder for the registered image to be saved
                output_dir = os.path.join(main_folder, sub_folder_derivatives, sub_folder_preproc, project, subject, session, 'pet')
                os.makedirs(output_dir, exist_ok=True)

                # name for the registered image
                pet_reg_filename = re.sub('rec-stat', 'pet-reg_rec-stat', filename_pet, flags=re.IGNORECASE)
                output_file = os.path.join(output_dir, pet_reg_filename)

                # register the moving image to the fixed image
                reg = ants.registration(fixed=fixed, moving=moving, type_of_transform='Rigid')
                ants.image_write(reg['warpedmovout'], filename=output_file)
                print(f'Registered: {pet_reg_filename}')

                # display the images
                if os.path.exists(output_file):
                    pet_img = nib.load(output_file)  # load the registered pet image
                    # visualise pet
                    plotting.plot_anat(pet_img, title=f'{pet_reg_filename}', display_mode='ortho', cut_coords=None,
                                       annotate=True, draw_cross=False, radiological=False)
                    plt.show()
                else:
                    print(f"No file: {output_file}")

            except Exception as e:
                print(e)

        else:
            print(f'{fixed_img} or {moving_img} not found')